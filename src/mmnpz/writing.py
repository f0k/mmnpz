"""
Support for sequentially writing uncompressed .npz files.
"""

__all__ = ["NpzWriter"]

from pathlib import Path
from typing import Literal, Union
from zipfile import ZipFile

import numpy as np
from numpy.typing import ArrayLike


class NpzWriter(object):
    """
    Helper class to sequentially add arrays to a given uncompressed .npz file.

    Parameters
    ----------
    fn : str or Path
        The zipped archive to replace, create, or append to.
    mode : str, optional
        The mode can be either write 'w', exclusive create 'x', or append 'a'.
        It defaults to 'x', so it will fail for existing files. Use 'w' to
        replace existing files, or 'a' to append to existing files.

    Examples
    --------
    Store data sequentially on disk, possibly overwriting an existing .npz file:

    >>> with mmnpz.NpzWriter("/tmp/123.npz", mode="w") as f:
    >>>     f.write("a", [[1, 2], [3, 4]])
    >>>     f.write("b", [5, 6, 7, 8])

    Append more data later:

    >>> with mmnpz.NpzWriter("/tmp/123.npz", mode="a") as f:
    >>>     f.write("c", [[9.5], [10.5]])

    Attributes
    ----------
    zip : ZipFile instance
        The ZipFile object for accessing the .npz file.
    """

    def __init__(self, fn: Union[str, Path], mode: Literal["w", "x", "a"] = "x") -> None:
        if mode not in ("w", "x", "a"):
            raise ValueError("NpzWriter requires mode 'w', 'x' or 'a', got %r" % mode)
        self.zip = ZipFile(fn, mode=mode)

    def write(self, name: str, array: ArrayLike) -> None:
        """
        Writes the given array under the given name.

        Parameters
        ----------
        name : str
            File name in the archive to save as, without its ``.npy`` extension.
            Supports directories separated by slashes.
        array : array-like
            Array to save to the file.
        """
        array = np.asanyarray(array)
        with self.zip.open(name + ".npy", "w", force_zip64=True) as f:
            np.lib.format.write_array(f, array, allow_pickle=False)

    def close(self) -> None:
        """
        Close the file.
        """
        if hasattr(self, "zip"):
            self.zip.close()
            del self.zip

    def __enter__(self) -> "NpzWriter":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def __del__(self):
        self.close()
