#! /usr/bin/python3
# -*- coding: utf-8 -*-

#####################################################################
# THE SOFTWARE IS PROVIDED AS IS WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#####################################################################
"""Testing functions for torrentfile module."""

import os
from pathlib import Path

import pytest

from tests.context import Temp, build, rmpath, testfile
from torrentfile import TorrentFile, TorrentFileHybrid, TorrentFileV2, utils
from torrentfile.torrent import MetaFile


@pytest.fixture(scope="module", params=Temp.structs)
def tdir1(request):
    """Return temporary directory."""
    folder = build(request.param)
    args = {"path": folder, "announce": "https://tracker.com/announce"}
    yield folder, args
    rmpath(folder)


@pytest.fixture
def smallfile():
    """Generate Sized file a tiny bit larger than BLOCK_SIZE."""
    path = testfile(exp=14)
    with open(path, "ab") as fd:
        fd.write(b"000000000000000")
    yield path
    rmpath(path)


def test_torrentfile_dir(tdir1):
    """Test temporary directory."""
    _, args = tdir1
    torrent = TorrentFile(**args)
    assert torrent.meta is not None  # nosec


def test_torrentfile_dir_private(tdir1):
    """Test temporary dir with arguments."""
    _, args = tdir1
    args["private"] = True
    args["piece_length"] = 1048576
    torrent = TorrentFile(**args)
    meta = torrent.meta
    assert "private" in meta["info"]  # nosec


def test_torrentfile_dir_comment(tdir1):
    """Test temporary dir with arguments."""
    _, args = tdir1
    args["private"] = True
    args["comment"] = "This is a comment"
    torrent = TorrentFile(**args)
    meta = torrent.meta
    assert "private" in meta["info"] and "comment" in meta["info"]  # nosec


def test_exception_path_error():
    """Test MissingPathError exception."""
    try:
        raise utils.MissingPathError("this is a message")
    except utils.MissingPathError:
        assert True  # nosec


def test_torrentfile_with_outfile(tdir1):
    """Test TorrentFile class with output in kwargs."""
    path, args = tdir1
    outfile = path + ".torrent"
    args["outfile"] = outfile
    torrent = TorrentFile(**args)
    torrent.write()
    assert os.path.exists(outfile)  # nosec
    rmpath(outfile)


def test_torrentfile_write_outfile(tdir1):
    """Test TorrentFile class with output in kwargs."""
    path, args = tdir1
    outfile = path + ".torrent"
    torrent = TorrentFile(**args)
    torrent.write(outfile=outfile)
    assert os.path.exists(outfile)  # nosec
    rmpath(outfile)


def test_torrentfilev2_outfile(tdir1):
    """Test TorrentFile2 class with output as argument."""
    path, args = tdir1
    outfile = path + ".torrent"
    torrent = TorrentFileV2(**args)
    torrent.write(outfile=outfile)
    assert os.path.exists(outfile)  # nosec
    rmpath(outfile)


def test_torrentfilev2_with_outfile(tdir1):
    """Test TorrentFileV2 class with output in kwargs."""
    path, args = tdir1
    outfile = path + ".torrent"
    args["outfile"] = outfile
    torrent = TorrentFileV2(**args)
    torrent.write()
    assert os.path.exists(outfile)  # nosec
    rmpath(outfile)


def test_hybrid_outfile(tdir1):
    """Test Hybrid class with output as argument."""
    path, args = tdir1
    outfile = path + ".torrent"
    torrent = TorrentFileHybrid(**args)
    torrent.write(outfile=outfile)
    assert os.path.exists(outfile)  # nosec
    rmpath(outfile)


def test_hybrid_with_outfile(tdir1):
    """Test Hybrid class with output in kwargs."""
    path, args = tdir1
    outfile = path + ".torrent"
    args["outfile"] = outfile
    torrent = TorrentFileHybrid(**args)
    torrent.write()
    assert os.path.exists(outfile)  # nosec
    rmpath(outfile)


def test_hybrid_0_length():
    """Test Hybrid with zero length file."""
    path = Path(Temp.root) / "empty"
    path.touch()
    args = {
        "path": str(path),
        "announce": "announce",
    }
    torrent = TorrentFileHybrid(**args)
    assert torrent.meta["announce"] == "announce"  # nosec
    torrent.write()
    torpath = path.with_suffix(".torrent")
    assert os.path.exists(torpath)   # nosec
    rmpath([path, torpath])


def test_v2_0_length():
    """Test TorrentFileV2 with zero length file."""
    path = Path(Temp.root) / "empty"
    path.touch()
    args = {
        "path": str(path),
        "announce": "announce",
    }
    torrent = TorrentFileV2(**args)
    torrent.write()
    torpath = path.with_suffix(".torrent")
    assert os.path.exists(torpath)  # nosec
    rmpath([path, torpath])


def test_metafile_assemble(tdir1):
    """Test MetaFile assemble file Exception."""
    fd, args = tdir1
    meta = MetaFile(**args)
    try:
        meta.assemble()
    except NotImplementedError:
        assert True   # nosec
    rmpath(fd)


def test_hybrid_sized_file(smallfile):
    """Test pad_remaining function in hybrid FileHash class."""
    args = {"path": smallfile, "announce": "announce", "piece_length": 15}
    torrent = TorrentFileHybrid(**args)
    assert torrent.meta["announce"] == args["announce"]      # nosec
    assert torrent.meta["info"]["piece length"] == 2 ** 15   # nosec


def test_hybrid_under_block_sized():
    """Test pad_remaining function in hybrid FileHash class."""
    smallest = os.path.join(Temp.root, "smallest")
    with open(smallest, "wb") as fd:
        letters = b"abcdefghijklmnopqrstuvwxyzABZDEFGHIJKLMNOPQRSTUVWXYZ"
        size = len(letters)
        while size < 16000:
            fd.write(letters)
            size += len(letters)
    args = {"path": smallest, "piece_length": 2**14}
    torrent = TorrentFileHybrid(**args)
    assert torrent.meta["info"]["piece length"] == 2 ** 14   # nosec
    rmpath(smallest)


def maketorrent(args, v=None):
    """Torrent making factory."""
    if v not in [2, 3]:
        torrent = TorrentFile(**args)
    elif v == 2:
        torrent = TorrentFileV2(**args)
    elif v == 3:
        torrent = TorrentFileHybrid(**args)
    torrent.assemble()
    return torrent.write()


@pytest.fixture(scope="module", params=Temp.structs)
def tdir(request):
    """Return temp directory."""
    return build(request.param)


@pytest.fixture(scope="module")
def metav3d(tdir):
    """Return generated metadata v2 for directory."""
    args = {
        "private": True,
        "path": tdir,
        "announce": "http://announce.com/announce",
        "source": "tracker",
        "comment": "content details and purpose",
    }
    outfile, meta = maketorrent(args, v=3)
    yield outfile, meta
    rmpath([tdir, outfile])


@pytest.fixture(scope="module")
def metav2d(tdir):
    """Return generated metadata v2 for directory."""
    args = {
        "private": True,
        "path": tdir,
        "announce": "http://announce.com/announce",
        "source": "tracker",
        "comment": "content details and purpose",
    }
    outfile, meta = maketorrent(args, v=2)
    yield outfile, meta
    rmpath([tdir, outfile])


@pytest.fixture(scope="module")
def metav1d(tdir):
    """Return generated metadata v1 for directory."""
    args = {
        "private": True,
        "path": tdir,
        "announce": "http://announce.com/announce",
        "source": "tracker",
        "comment": "content details and purpose",
    }
    outfile, meta = maketorrent(args)
    yield outfile, meta
    rmpath([tdir, outfile])


@pytest.mark.parametrize('key', ["announce", "info", "piece layers",
                                 "creation date", "created by"])
def test_v2_meta_keys(metav2d, key):
    """Test metadata."""
    outfile, meta = metav2d
    assert key in meta  # nosec
    assert os.path.exists(outfile)  # nosec


@pytest.mark.parametrize('field', ["announce", "info", "piece layers",
                                   "creation date", "created by"])
def test_v3_meta_keys(metav3d, field):
    """Test metadata."""
    outfile, meta = metav3d
    assert field in meta  # nosec
    assert os.path.exists(outfile)  # nosec


@pytest.mark.parametrize('key', ["piece length", "meta version", "file tree",
                                 "name", "private", "source", "comment"])
def test_v2_info_keys_dir(metav2d, key):
    """Test metadata."""
    outfile, meta = metav2d
    assert key in meta["info"]  # nosec
    assert os.path.exists(outfile)  # nosec


@pytest.mark.parametrize('field', ["piece length", "meta version", "file tree",
                                   "name", "private", "source", "comment"])
def test_v3_info_keys_dir(metav3d, field):
    """Test metadata."""
    outfile, meta = metav3d
    assert field in meta["info"]  # nosec
    assert os.path.exists(outfile)  # nosec


@pytest.mark.parametrize('key', ["announce", "info",
                                 "creation date", "created by"])
def test_v1_meta_keys(metav1d, key):
    """Test metadata."""
    outfile, meta = metav1d
    assert key in meta  # nosec
    assert os.path.exists(outfile)  # nosec


@pytest.mark.parametrize('key', ["piece length", "name", "private",
                                 "source", "comment", "pieces"])
def test_v1_info_keys_dir(metav1d, key):
    """Test metadata."""
    outfile, meta = metav1d
    assert key in meta["info"]  # nosec
    assert os.path.exists(outfile)  # nosec


@pytest.mark.parametrize('key', ["piece length", "name", "private",
                                 "source", "comment", "pieces"])
def test_v3_info_keys_pieces(metav3d, key):
    """Test metadata."""
    outfile, meta = metav3d
    assert key in meta["info"]  # nosec
    assert os.path.exists(outfile)  # nosec


def test_meta_no_args_v2():
    """Test construct TorrentFileV2 with no arguments."""
    try:
        assert TorrentFileV2(private=True)   # nosec
    except utils.MissingPathError:
        assert True  # nosec


def test_meta_no_args_v1():
    """Test construct TorrentFile with no arguments."""
    try:
        assert TorrentFile(announce="url")   # nosec
    except utils.MissingPathError:
        assert True  # nosec
