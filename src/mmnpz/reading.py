"""
Support for reading memory-mapped uncompressed .npz files.
"""

__all__ = ["NpzReader", "load"]

import struct
from collections.abc import Mapping
from pathlib import Path
from typing import Dict, Iterator, List, Literal, Tuple, Union
from zipfile import ZipFile

import numpy as np
from typing_extensions import Buffer


class NpzReader(Mapping):
    """
    A dictionary-like object with lazy-loading of numpy arrays in the given
    uncompressed .npz file. Upon construction, creates a memory map of the
    full .npz file, returning views for the arrays within on request. Serves
    as a drop-in replacement for :func:`numpy.load`.

    Parameters
    ----------
    fn : str or Path
        The zipped archive to open.
    mmap_mode : str, optional
        Provided for compatibility with numpy. Only supports 'r', indicating
        that the file is loaded as a readonly memory map.
    cache : bool, optional
        Whether to cache array objects in case they are requested again.
    preload : bool, optional
        Whether to precreate all array objects upon opening. Enforces caching.

    Raises
    ------
    OSError
        If the input file does not exist or cannot be read.
    zipfile.BadZipFile
        If the input file cannot be interpreted as a zip file.

    Examples
    --------
    Store data to disk, and load it again as a memory map:

    >>> np.savez("/tmp/123.npz", a=np.array([[1, 2], [3, 4]]))
    >>> data = mmnpz.NpzReader("/tmp/123.npz")
    >>> data["a"]
    memmap([[1, 2],
            [3, 4]])

    Attributes
    ----------
    files : list of str
        List of all uncompressed files in the archive with a ``.npy`` extension
        (listed without the extension). These are supported as dictionary keys.
    mmap : numpy.memmap
        The memory map of the full .npz file.
    arrays : dict
        Preloaded or cached arrays.
    """

    def __init__(
        self,
        fn: Union[str, Path],
        mmap_mode: Literal["r"] = "r",
        *,
        cache: bool = True,
        preload: bool = False,
    ) -> None:
        if mmap_mode != "r":
            raise ValueError("NpzReader requires mmap_mode='r', got %r" % mmap_mode)
        with ZipFile(fn, mode="r") as f:
            self._offsets: Dict[str, Tuple[int, int]] = {
                zinfo.filename[:-4]: (zinfo.header_offset, zinfo.file_size)
                for zinfo in f.infolist()
                if zinfo.filename.endswith(".npy") and zinfo.compress_type == 0
            }
        self.files: List[str] = list(self._offsets.keys())
        self.mmap = np.memmap(fn, mode="r")
        self.cache = cache or preload
        self.preload = preload
        self.arrays: Dict[str, np.memmap]
        if self.preload:
            self.arrays = {name: self.load(name) for name in self.files}
        else:
            self.arrays = {}

    def load(self, name: str) -> np.memmap:
        """
        Creates a view for the specified array, disregarding the cache.

        Parameters
        ----------
        name : str
            File name in the archive to load, without its ``.npy`` extension.

        Returns
        -------
        numpy.memmap
            A view into the global memory map with correct shape and dtype.

        See also
        --------
        __getitem__ : Returns a view for the specified array using the cache.
        """
        header_offset, file_size = self._offsets[name]
        # parse lengths of local header file name and extra fields
        # (ZipInfo is based on the global directory, not local header)
        fn_len, extra_len = struct.unpack("<2H", self.mmap[header_offset + 26 : header_offset + 30])
        # compute offset of start and end of data
        npy_start = header_offset + 30 + fn_len + extra_len
        npy_end = npy_start + file_size
        # read NPY header
        fp = MemoryviewIO(self.mmap)
        fp.seek(npy_start)
        version = np.lib.format.read_magic(fp)
        np.lib.format._check_version(version)
        shape, fortran, dtype = np.lib.format._read_array_header(fp, version)
        # produce slice of memmap
        data_start = fp.tell()
        return (
            self.mmap[data_start:npy_end]
            .view(dtype=dtype)
            .reshape(shape, order="F" if fortran else "C")
        )

    def close(self) -> None:
        """
        Releases the memory map and any cached views.
        """
        if hasattr(self, "mmap"):
            del self.mmap
        self.arrays = {}

    def __enter__(self) -> "NpzReader":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def __iter__(self) -> Iterator[str]:
        return iter(self.files)

    def __len__(self) -> int:
        return len(self.files)

    def __getitem__(self, key: str) -> np.memmap:
        if self.cache:
            try:
                return self.arrays[key]
            except KeyError:
                pass
        array = self.load(key)
        if self.cache:
            self.arrays[key] = array
        return array

    def __contains__(self, key: object) -> bool:
        # Mapping.__contains__ calls __getitem__, which could be expensive
        return key in self._offsets


load = NpzReader  # Alias for serving as a :func:`numpy.load` replacement


class MemoryviewIO(object):
    """
    Wraps an object supporting the buffer protocol to be a readonly file-like.
    """

    def __init__(self, buffer: Buffer):
        self._buffer = memoryview(buffer).cast("B")
        self._pos = 0
        self.seekable = lambda: True
        self.readable = lambda: True
        self.writable = lambda: False

    def seek(self, offset: int, whence: int = 0):
        if whence == 0:
            self._pos = offset
        elif whence == 1:
            self._pos += offset
        elif whence == 2:
            self._pos = self._buffer.nbytes + offset

    def read(self, size: int = -1) -> bytes:
        data = self._buffer[self._pos : self._pos + size if size >= 0 else None].tobytes()
        self._pos += len(data)
        return data

    def tell(self) -> int:
        return self._pos
