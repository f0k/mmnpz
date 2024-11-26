mmnpz
=====

**mmnpz** is a small Python package for handling large .npz files.
.npz files are uncompressed zip files containing numpy arrays.
**mmnpz** unlocks their potential as an efficient, standardized
option for storing and accessing large datasets.

Usage
-----

**mmnpz** can write large .npz files incrementally:

```python
>>> import numpy as np
>>> import mmnpz
>>> with mmnpz.NpzWriter("test.npz") as f:
>>>     for i in range(10):
>>>         f.write(f"a{i}", np.full(10000, i))
```

**mmnpz** can read large .npz files as memory maps:

```python
>>> import mmnpz
>>> x = mmnpz.load("test.npz")
>>> x["a2"][10:15]
memmap([2, 2, 2, 2, 2])
```

This allows accessing individual excerpts of large datasets [without I/O
overhead](background.md).

Documentation
-------------

* User guide: [installation](installation.md), [usage](usage.md) and [background](background.md)
* Reference: functions and classes for [writing](writing.md) and [reading](reading.md)
* Development: [change log](CHANGELOG.md), [contributor's guide](CONTRIBUTING.md) and [git repository](https://github.com/f0k/mmnpz)

```{toctree}
:hidden:

Overview <self>
```

```{toctree}
:maxdepth: 2
:hidden:
:caption: User guide

installation
usage
background
```

```{toctree}
:maxdepth: 2
:hidden:
:caption: Reference

writing
reading
```

```{toctree}
:hidden:
:caption: Development

CHANGELOG
CONTRIBUTING
LICENSE
GitHub Repository <https://github.com/f0k/mmnpz>
```
