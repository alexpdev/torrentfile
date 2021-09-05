import os
import pytest
from torrentfile.metafileV2 import TorrentFileV2
from tests.context import TD, fill_folder, fill_file, rmpath

@pytest.fixture(scope="module")
def tempdir():
    tdir = os.path.join(TD, "tempdir")
    tdir_1 = os.path.join(tdir,"directory1")
    for folder in [tdir, tdir_1]:
        os.mkdir(folder)
        fill_folder(folder)
    yield tdir
    rmpath(tdir)

@pytest.fixture
def tempfile():
    path = os.path.join(TD,"tempfile.bin")
    fill_file(path)
    yield path
    rmpath(path)


def test_torrentfileV2(tempdir):
    args = {"private": True, "path": tempdir, "announce": "http://announce.com/announce"}
    torrent = TorrentFileV2(**args)
    torrent.assemble()
    outfile, meta = torrent.write()
    assert os.path.exists(outfile)
