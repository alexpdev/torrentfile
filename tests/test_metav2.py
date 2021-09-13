import os
import pytest
from torrentfile.metafileV2 import TorrentFileV2
from tests.context import tempdir, tempfile, rmpath


@pytest.fixture(scope="module")
def tfile():
    testfile = tempfile()
    yield testfile
    rmpath(testfile)


@pytest.fixture(scope="module")
def tdir():
    testdir = tempdir()
    yield testdir
    rmpath(testdir)


@pytest.fixture(scope="module")
def metav2f(tfile):
    args = {"private": True, "path": tfile, "announce": "http://announce.com/announce"}
    torrent = TorrentFileV2(**args)
    torrent.assemble()
    outfile, meta = torrent.write()
    yield outfile, meta
    rmpath(outfile)


@pytest.fixture(scope="module")
def metav2d(tdir):
    args = {
        "private": True,
        "path": tdir,
        "announce": "http://announce.com/announce",
        "source": "tracker",
        "comment": "content details and purpose",
    }
    torrent = TorrentFileV2(**args)
    torrent.assemble()
    outfile, meta = torrent.write()
    yield outfile, meta
    rmpath(outfile)


def test_v2_meta_keys(metav2f):
    outfile, meta = metav2f
    for key in ["announce", "info", "piece layers", "creation date", "created by"]:
        assert key in meta
    assert os.path.exists(outfile)


def test_v2_info_keys_file(metav2f):
    outfile, meta = metav2f
    for key in [
        "length",
        "piece length",
        "meta version",
        "file tree",
        "name",
        "private",
    ]:
        assert key in meta["info"]
    assert os.path.exists(outfile)


def test_v2_info_keys_dir(metav2d):
    outfile, meta = metav2d
    for key in [
        "piece length",
        "meta version",
        "file tree",
        "name",
        "private",
        "source",
        "comment",
    ]:
        assert key in meta["info"]
    assert os.path.exists(outfile)
