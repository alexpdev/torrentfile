import os
import pytest
from torrentfile.metafileV2 import TorrentFileV2
from torrentfile.metafile import TorrentFile, Checker
from tests.context import tempdir, tempfile, rmpath, Flags

@pytest.fixture(scope="module")
def metav2f():
    tfile = tempfile()
    args = {"private": True, "path": tfile, "announce": "http://announce.com/announce"}
    flags = Flags(**args)
    torrent = TorrentFileV2(flags)
    torrent.assemble()
    outfile, meta = torrent.write()
    yield outfile, meta
    rmpath(outfile)


@pytest.fixture(scope="module")
def metav2d():
    tdir = tempdir()
    args = {
        "private": True,
        "path": tdir,
        "announce": "http://announce.com/announce",
        "source": "tracker",
        "comment": "content details and purpose",
    }
    flags = Flags(**args)
    torrent = TorrentFileV2(flags)
    torrent.assemble()
    outfile, meta = torrent.write()
    yield outfile, meta
    rmpath(outfile)


@pytest.fixture(scope="module")
def metav1d():
    tdir = tempdir()
    args = {
        "private": True,
        "path": tdir,
        "announce": "http://announce.com/announce",
        "source": "tracker",
        "comment": "content details and purpose",
    }
    flags = Flags(**args)
    torrent = TorrentFile(flags)
    torrent.assemble()
    outfile, meta = torrent.write()
    yield outfile, meta
    rmpath(outfile)


@pytest.fixture(scope="module")
def metav1f():
    tfile = tempfile()
    args = {"private": True, "path": tfile,
            "announce": "http://announce.com/announce"}
    flags = Flags(**args)
    torrent = TorrentFile(flags)
    torrent.assemble()
    outfile, meta = torrent.write()
    yield outfile, meta
    rmpath(outfile)

@pytest.fixture(scope="module")
def tfilemeta():
    tfile = tempfile()
    args = {"private": True, "path": tfile,
            "announce": "http://announce.com/announce"}
    flags = Flags(**args)
    torrent = TorrentFile(flags)
    torrent.assemble()
    outfile, _ = torrent.write()
    yield outfile, tfile
    rmpath(outfile)

@pytest.fixture(scope="module")
def tdirmeta():
    tdir = tempdir()
    args = {"private": True, "path": tdir,
            "announce": "http://announce.com/announce"}
    flags = Flags(**args)
    torrent = TorrentFile(flags)
    torrent.assemble()
    outfile, _ = torrent.write()
    yield outfile, tdir
    rmpath(outfile)


def test_v2_meta_keys(metav2f):
    outfile, meta = metav2f
    for key in ["announce", "info", "piece layers",
                "creation date", "created by"]:
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


def test_v1_meta_keys(metav1f):
    outfile, meta = metav1f
    for key in ["announce", "info", "creation date", "created by"]:
        assert key in meta
    assert os.path.exists(outfile)


def test_v1_info_keys_file(metav1f):
    outfile, meta = metav1f
    for key in [
        "length",
        "piece length",
        "pieces",
        "name",
        "private",
    ]:
        assert key in meta["info"]
    assert os.path.exists(outfile)


def test_v1_info_keys_dir(metav1d):
    outfile, meta = metav1d
    for key in [
        "piece length",
        "pieces",
        "name",
        "private",
        "source",
        "comment",
    ]:
        assert key in meta["info"]
    assert os.path.exists(outfile)


def test_metafile_checker_v1_file(tfilemeta):
    outfile, tfile = tfilemeta
    checker = Checker(outfile, tfile)
    status = checker.check()
    assert status == "100%"

def test_metafile_checker_v1_dir(tdirmeta):
    outfile, tdir = tdirmeta
    checker = Checker(outfile, tdir)
    status = checker.check()
    assert status == "100%"
