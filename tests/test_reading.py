import zipfile

import numpy as np
import pytest

import mmnpz


@pytest.fixture(scope="session")
def good_npz(tmp_path_factory):
    fn = tmp_path_factory.mktemp("data") / "good.npz"
    np.savez(fn, a=np.array([[1, 2], [3, 4]]), b=np.linspace(0, 1, 6))
    return fn


@pytest.fixture(scope="session")
def bad_npz(tmp_path_factory):
    fn = tmp_path_factory.mktemp("data") / "bad.npz"
    with open(fn, "wb") as f:
        f.write(b"bad")
    return fn


@pytest.fixture(scope="session")
def absent_npz(tmp_path_factory):
    return tmp_path_factory.mktemp("data") / "absent.npz"


@pytest.mark.parametrize("preload", [False, True])
@pytest.mark.parametrize("cache", [False, True])
def test_read_success(good_npz, cache, preload):
    numpy = np.load(good_npz)
    ours = mmnpz.NpzReader(good_npz, cache=cache, preload=preload)
    assert len(numpy) == len(ours)
    assert numpy.files == list(ours)
    assert numpy.files == ours.files
    for key in numpy:
        assert key in ours
        assert isinstance(ours[key], np.memmap)
        assert np.array_equal(numpy[key], ours[key])
    assert "them" not in ours


def test_read_fail(bad_npz, absent_npz):
    with pytest.raises(zipfile.BadZipFile):
        mmnpz.NpzReader(bad_npz)
    with pytest.raises(IOError):
        mmnpz.NpzReader(absent_npz)


def test_cache(good_npz):
    data = mmnpz.NpzReader(good_npz)
    assert len(data.arrays) == 0
    a = data["a"]
    assert data.arrays == {"a": a}
    b = data["b"]
    assert data.arrays == {"a": a, "b": b}
    # check that repeated access gives the same view
    assert data["a"] is a
    assert data["b"] is b


def test_preload(good_npz):
    numpy = np.load(good_npz)
    ours = mmnpz.NpzReader(good_npz, preload=True)
    ours_preloaded = ours.arrays
    for key in numpy:
        assert key in ours_preloaded
        assert np.array_equal(numpy[key], ours_preloaded[key])


def test_nocache(good_npz):
    data = mmnpz.NpzReader(good_npz, cache=False)
    # check that every access creates a new view
    assert data["a"] is not data["a"]


def test_mmap(good_npz):
    data = mmnpz.NpzReader(good_npz)
    assert isinstance(data.mmap, np.memmap)
    assert data["a"].base is data.mmap


def test_close(good_npz):
    data = mmnpz.NpzReader(good_npz)
    _ = data["a"]
    assert hasattr(data, "mmap")
    assert len(data.arrays) > 0
    data.close()
    assert not hasattr(data, "mmap")
    assert len(data.arrays) == 0


def test_context_manager(good_npz):
    with mmnpz.NpzReader(good_npz) as data:
        _ = data["a"]
    assert not hasattr(data, "mmap")
    assert len(data.arrays) == 0


def test_memoryviewio():
    m = mmnpz.reading.MemoryviewIO(b"abcd")
    assert m.tell() == 0
    assert m.read(1) == b"a"
    assert m.tell() == 1
    m.seek(0)
    assert m.tell() == 0
    assert m.read(1) == b"a"
    assert m.tell() == 1
    m.seek(2)
    assert m.tell() == 2
    assert m.read(1) == b"c"
    assert m.tell() == 3
    m.seek(-2, 1)
    assert m.tell() == 1
    assert m.read(2) == b"bc"
    assert m.tell() == 3
    m.seek(0, 2)
    assert m.tell() == 4
    assert m.read() == b""


def test_unsupported_mmap_mode(good_npz):
    with pytest.raises(ValueError):
        mmnpz.NpzReader(good_npz, mmap_mode="w")  # type: ignore
