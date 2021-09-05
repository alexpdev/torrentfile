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
def metav2(tfile):
    args = {"private": True, "path": tfile, "announce": "http://announce.com/announce"}
    torrent = TorrentFileV2(**args)
    torrent.assemble()
    outfile, meta = torrent.write()
    yield outfile, meta
    rmpath(outfile)

def test_v2_meta_keys(metav2):
    outfile, meta = metav2
    for key in ["announce", "info", "piece layers", "creation date"]:
        assert key in meta
    assert os.path.exists(outfile)

def test_v2_info_keys(metav2):
    outfile, meta = metav2
    for key in ["length", "piece length", "file_tree", "meta version"]:
        assert key in meta["info"]
    assert os.path.exists(outfile)
