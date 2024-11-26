Background
==========

To understand what problem **mmnpz** solves, we will look at a use case. If you
are fully familiar with memory maps, you can skip this, and only look at the
[implementation](#implementation) section.

## Use case

Assume you are training a machine learning model on short excerpts of a large
collection of audio files. The audio files are preprocessed into spectrograms,
which are 2-dimensional matrices, with time in the first dimension. On each
iteration over the dataset, you want to process one temporal excerpt of each
spectrogram.

## Naive way

Naively, you could save each audio file as a .npy file. To produce excerpts for
a training iteration, you load the .npy files in random order and pick random
excerpts:

```python
def get_excerpts(filenames: list[str], excerpt_length: float, rng: np.random.Generator):
    for idx in rng.permutation(len(filenames)):
        x = np.load(filenames[idx])
        start = rng.integers(len(x) - excerpt_length)
        yield x[start:start + excerpt_length]
```

This is inefficient: {py:func}`numpy.load` reads the full .npy file from disk into
memory, only to return a short excerpt.

## Memory maps

To improve on the previous recipe, instead of reading the .npy file into
memory, you can create a read-only memory map of the .npy file by passing
`mmap_mode="r"`:

```python
def get_excerpts(filenames: list[str], excerpt_length: float, rng: np.random.Generator):
    for idx in rng.permutation(len(filenames)):
        x = np.load(filenames[idx], mmap_mode="r")
        start = rng.integers(len(x) - excerpt_length)
        yield x[start:start + excerpt_length]
```

A memory map is a construct provided by the operating system that ties a range
of your process's memory addresses to a file on the disk. Only when your
process reads any of the addresses, the data is transferred from disk to
physical memory. In this case, the {py:func}`numpy.load` call only establishes
the memory map, and the `x[start:start + excerpt_length]` creates a view into a
slice of that map. Only when the callee performs computations with the array
contents, the required part of the .npy file is loaded from disk. The operating
system is free to cache parts of previously accessed .npy files if enough main
memory is available.

Memory maps are an elegant way of loading data from disk lazily. All the logic
of when to load what part of the data and what to keep in the cache is
offloaded to the operating system. However, the above recipe is still a bit
inefficient in that it queries the file system for every excerpt to return.

## Precreated memory maps

To avoid the file system overhead, you may create all memory maps in advance:

```python
maps = [np.load(fn, mmap_mode="r") for fn in filenames]
```

And then access the maps in the excerpt generator:

```python
def get_excerpts(maps: list[np.typing.ArrayLike], excerpt_length: float, rng: np.random.Generator):
    for idx in rng.permutation(len(filenames)):
        x = maps[idx]
        start = rng.integers(len(x) - excerpt_length)
        yield x[start:start + excerpt_length]
```

However, each memory map requires holding an open file descriptor, and for
performance reasons, operating systems usually place restrictions on how many
open file descriptors each process can hold. Thus, this recipe does not scale.

## Single memory map

If you could concatenate all your .npy files into a single file, along with
some index that allows you to find each one, you could open a single memory map
and then create slices of the memory map to represent each item. This is what
**mmnpz** provides. You can create a .npz file in advance:

```python
with mmnpz.NpzWriter("dataset.npz") as f:
    for fn in filenames:
        f.write(fn, np.load(fn))
```

Load it once:

```python
data = mmnpz.load("dataset.npz")
```

And then use it in the excerpt generator:

```python
def get_excerpts(data: mmnpz.NpzReader, excerpt_length: float, rng: np.random.Generator):
    for idx in rng.permutation(len(data)):
        x = data[data.files[idx]]
        start = rng.integers(len(x) - excerpt_length)
        yield x[start:start + excerpt_length]
```

This recipe retains the advantages of memory maps, but avoids the file system
overhead.

## Implementation

**mmnpz** chooses to use the .npz format as the container for multiple numpy
arrays. A .npz file is a ZIP file of .npy files. If the .npy files are stored
uncompressed (as when written with {py:func}`numpy.savez` or
{py:class}`mmnpz.NpzWriter`), their data is included 1:1 in the .npz file. The
ZIP format also includes a global index specifying the name and location of
each .npy file within.

When you instantiate a {py:class}`mmnpz.NpzReader`, it creates a memory map of
the full .npz file and reads its global index to find the names and offsets of
all uncompressed .npy members. When you access a member by name for the first
time, it looks at the associated offset and reads the local ZIP header to find
the starting position of the .npy file. Finally, it parses the header of the
.npy file to find the shape, dtype, memory layout and offset of the actual
array data and creates a corresponding view of the full memory map to return.
By default, this view is cached to speed up future queries. All parsing of ZIP
and .npy headers uses the memory map rather than file descriptors, making the
implementation safe for multithreading and multiprocessing.

## Caveats

**Alignment**: ZIP files sequentially store the local header and data of each
member, followed by a global index in the end that usually copies the local
headers. The offset each numpy array starts at thus depends on the sizes of all
local headers and members that came before, and will often not be aligned to
the word size of the array data. It would be possible to fix this by [adding
alignment bytes](https://issues.apache.org/jira/browse/COMPRESS-391) to the
local header extra data, with the small downside that {py:mod}`zipfile` would
unnecessarily copy the alignment bytes over to the global index, as it does
not distinguish local and global extra data.

**I/O overhead**: To create a view for a member requested by name,
**mmnpz** needs to read its .npy header, which requires a local read inside the
.npz file. This incurs some overhead, which is why by default, this step is
delayed until a member is actually requested (at which time the member's nearby
data will probably be need to read anyway). It would be possible to fix this
by including the .npy header in the global index extra data, with the downside
that {py:mod}`zipfile` would unnecessarily copy this over to the local header,
as it does not distinguish local and global extra data.

## Alternatives

**mmnpz** is by far not the first implementation for this recipe, but one of
the simplest. It does not invent a custom format such as
[mmap.ninja](https://github.com/hristo-vrigazov/mmap.ninja), but uses existing
standards. It does not attempt to compete with mightier alternatives such as
[Hugging Face Datasets](https://huggingface.co/docs/datasets/index), which is
based on [Apache Arrow](https://arrow.apache.org/) and has extra features such
as splitting large datasets into multiple disk files or streaming over HTTP.
If you already use an alternative, there is no point in switching to **mmnpz**.
If, however, you just need to move your pipeline to something more efficient,
**mmnpz** may be easier to learn, set up and try than others.
