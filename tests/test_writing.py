import numpy as np
import pytest

import mmnpz


def make_arrays(k: int = 5):
    for i in range(k):
        yield str(i), np.full(i, i)


def save_arrays(fn, *, k: int = 5, **kwargs):
    with mmnpz.NpzWriter(fn, **kwargs) as f:
        for key, array in make_arrays(k):
            f.write(key, array)


@pytest.fixture
def npz_file(tmp_path):
    fn = tmp_path / "test.npz"
    save_arrays(fn)
    return fn


def test_savez_success(npz_file):
    with np.load(npz_file) as data:
        for key, array in make_arrays():
            assert key in data
            assert np.array_equal(data[key], array)


def test_exclusive(npz_file, tmp_path):
    with pytest.raises(IOError):
        with mmnpz.writing.NpzWriter(npz_file):
            pass
    with mmnpz.writing.NpzWriter(tmp_path / "test2.npz"):
        pass


def test_overwrite(npz_file):
    save_arrays(npz_file, k=3, mode="w")
    with np.load(npz_file) as data:
        assert len(data) == 3
        for key, array in make_arrays(3):
            assert key in data
            assert np.array_equal(data[key], array)


def test_append(npz_file):
    with mmnpz.writing.NpzWriter(npz_file, mode="a") as f:
        f.write("5", np.full(5, 5))
    with np.load(npz_file) as data:
        for key, array in make_arrays(6):
            assert key in data
            assert np.array_equal(data[key], array)


def test_unsupported_mode(tmp_path):
    with pytest.raises(ValueError):
        mmnpz.writing.NpzWriter(tmp_path / "test.npz", mode="r")  # type: ignore
