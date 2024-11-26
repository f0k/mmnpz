Usage
=====

**mmnpz** can write and read .npz files too large to fit into main memory.
Files are fully compatible with {py:func}`numpy.savez` and {py:func}`numpy.load`.

Writing
-------

Assuming you create or process a dataset of many items in a loop, you can write
them to a .npz file using an {py:class}`mmnpz.NpzWriter`:

```python
import mmnpz
with mmnpz.NpzWriter("dataset.npz") as f:
    for name in names:
        # load and process an item of your large dataset, then:
        f.write(name, data)
```

You may also append items to an existing file:

```python
with mmnpz.NpzWriter("dataset.npz", mode="a") as f:
    f.write("more", [1, 2, 3])
```

If using {py:class}`mmnpz.NpzWriter` as a context manager is inconvenient for
your use case, create and close it manually:

```python
f = mmnpz.NpzWriter("dataset.npz")
f.write("something", [[1, 2], [3, 4]])
f.close()
```

For all the details, see the [API reference for writing](writing.md).

Reading
-------

To read a .npz file, use an {py:class}`mmnpz.NpzReader`, a drop-in replacement
for {py:func}`numpy.load` for uncompressed, unpickled .npz files. For
convenience, it is also available as {py:func}`mmnpz.load`:

```python
data = mmnpz.load("dataset.npz")
x = data["something"]
```

Under the hood, {py:class}`mmnpz.NpzReader` creates a memory map of the full
.npz file, and then creates a view of the correct portion for every item that
is requested. By default, these views are cached, to speed up repeated access
of the same item. If you know each item will only be accessed once, you can
disable this behavior:

```python
data = mmnpz.load("dataset.npz", cache=False)
```

If you know you will need to access every single item, you may also opt to
create all views upon loading the file:

```python
data = mmnpz.load("dataset.npz", preload=True)
```

Note that this requires reading the file headers of each included numpy array,
which are spread across the file. The default behavior (caching, but no
preloading) results in more localized disk access, as each header is read when
the corresponding nearby data is requested for the first time.

{py:class}`mmnpz.NpzReader` provides a dictionary-like interface to the arrays
contained within. If you need an actual dictionary instead, the
{py:attr}`mmnpz.NpzReader.arrays` attribute provides direct access to all
preloaded or cached items:

```python
data = mmnpz.load("dataset.npz", preload=True)
data = data.arrays
```

Again, for details, see the [API reference for reading](reading.md).
