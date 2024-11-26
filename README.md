mmnpz
=====

[![PyPI: Version](https://img.shields.io/pypi/v/mmnpz)](https://pypi.org/project/mmnpz/)
[![Documentation](https://readthedocs.org/projects/mmnpz/badge/?version=latest)](https://mmnpz.readthedocs.io/en/latest/)
[![Tests](https://github.com/f0k/mmnpz/actions/workflows/tests.yml/badge.svg)](https://github.com/f0k/mmnpz/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.md)

**mmnpz** is a small Python package for handling large .npz files.
.npz files are uncompressed zip files containing numpy arrays.
**mmnpz** unlocks their potential as an efficient, standardized
option for storing and accessing large datasets.

Installation
------------

**mmnpz** is available [on PyPI](https://pypi.org/project/mmnpz/).
To install the latest release, run:

```bash
pip install mmnpz
```

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
overhead](https://mmnpz.readthedocs.io/en/latest/background.html).

Documentation
-------------

The documentation is hosted on [readthedocs](https://mmnpz.readthedocs.io).

Acknowledgements
----------------

The package layout and toolchain is based on
[Ai2's Python package template](https://github.com/allenai/python-package-template),
[Microsoft's Python package template](https://github.com/microsoft/python-package-template/) and
[pytest's Python package](https://github.com/pytest-dev/pytest/).
The package was developed at the
[Institute of Computational Perception](https://www.cp.jku.at),
[Johannes Kepler University Linz](https://www.jku.at).
