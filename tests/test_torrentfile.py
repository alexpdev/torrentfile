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

from tests.context import TESTDIR, parameters, rmpath, rmpaths, sizedfile
from torrentfile import TorrentFile, TorrentFileHybrid, TorrentFileV2
from torrentfile.utils import MetaFile, MissingPathError


@pytest.fixture(scope="module", params=parameters())
def tdir(request):
    """Return temporary directory."""
    folder = request.param()
    args = {"path": folder, "announce": "https://tracker.com/announce"}
    yield (folder, args)
    rmpath(folder)


@pytest.fixture
def smallfile():
    """Generate Sized file a tiny bit larger than BLOCK_SIZE."""
    path = sizedfile(14)
    with open(path, "ab") as fd:
        fd.write(b"000000000000000")
    yield path
    rmpath(path)


def test_torrentfile_dir(tdir):
    """Test temporary directory."""
    _, args = tdir
    torrent = TorrentFile(**args)
    assert torrent.meta is not None  # nosec


def test_torrentfile_dir_private(tdir):
    """Test temporary dir with arguments."""
    _, args = tdir
    args["private"] = True
    args["piece_length"] = 1048576
    torrent = TorrentFile(**args)
    meta = torrent.meta
    assert "private" in meta["info"]  # nosec


def test_torrentfile_dir_comment(tdir):
    """Test temporary dir with arguments."""
    _, args = tdir
    args["private"] = True
    args["comment"] = "This is a comment"
    torrent = TorrentFile(**args)
    meta = torrent.meta
    assert "private" in meta["info"] and "comment" in meta["info"]  # nosec


def test_exception_path_error():
    """Test MissingPathError exception."""
    try:
        raise MissingPathError("this is a message")
    except MissingPathError:
        assert True  # nosec


def test_torrentfile_with_outfile(tdir):
    """Test TorrentFile class with output in kwargs."""
    path, args = tdir
    outfile = path + ".torrent"
    args["outfile"] = outfile
    torrent = TorrentFile(**args)
    torrent.write()
    assert os.path.exists(outfile)  # nosec
    rmpath(outfile)


def test_torrentfilev2_outfile(tdir):
    """Test TorrentFile2 class with output as argument."""
    path, args = tdir
    outfile = path + ".torrent"
    torrent = TorrentFileV2(**args)
    torrent.write(outfile=outfile)
    assert os.path.exists(outfile)  # nosec
    rmpath(outfile)


def test_torrentfilev2_with_outfile(tdir):
    """Test TorrentFileV2 class with output in kwargs."""
    path, args = tdir
    outfile = path + ".torrent"
    args["outfile"] = outfile
    torrent = TorrentFileV2(**args)
    torrent.write()
    assert os.path.exists(outfile)  # nosec
    rmpath(outfile)


def test_hybrid_outfile(tdir):
    """Test Hybrid class with output as argument."""
    path, args = tdir
    outfile = path + ".torrent"
    torrent = TorrentFileHybrid(**args)
    torrent.write(outfile=outfile)
    assert os.path.exists(outfile)  # nosec
    rmpath(outfile)


def test_hybrid_with_outfile(tdir):
    """Test Hybrid class with output in kwargs."""
    path, args = tdir
    outfile = path + ".torrent"
    args["outfile"] = outfile
    torrent = TorrentFileHybrid(**args)
    torrent.write()
    assert os.path.exists(outfile)  # nosec
    rmpath(outfile)


def test_hybrid_0_length():
    """Test Hybrid with zero length file."""
    path = Path(TESTDIR) / "empty"
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
    rmpaths([path, torpath])


def test_v2_0_length():
    """Test TorrentFileV2 with zero length file."""
    path = Path(TESTDIR) / "empty"
    path.touch()
    args = {
        "path": str(path),
        "announce": "announce",
    }
    torrent = TorrentFileV2(**args)
    torrent.write()
    torpath = path.with_suffix(".torrent")
    assert os.path.exists(torpath)  # nosec
    rmpaths([path, torpath])


def test_metafile_assemble(tdir):
    """Test MetaFile assemble file Exception."""
    fd, args = tdir
    meta = MetaFile(**args)
    try:
        meta.assemble()
    except NotImplementedError:
        assert True   # nosec
    rmpath(fd)


def test_metafile_write(tdir):
    """Test MetaFile write Exception."""
    fd, args = tdir
    meta = MetaFile(**args)
    try:
        meta.write()
    except NotImplementedError:
        assert True   # nosec
    rmpath(fd)


def test_hybrid_sized_file(smallfile):
    """Test pad_remaining function in hybrid FileHash class."""
    args = {"path": smallfile, "announce": "announce", "piece_length": 2**14}
    torrent = TorrentFileHybrid(**args)
    assert torrent.meta["announce"] == args["announce"]      # nosec
    assert torrent.meta["info"]["piece length"] == 2 ** 14   # nosec


def test_hybrid_under_block_sized():
    """Test pad_remaining function in hybrid FileHash class."""
    smallest = os.path.join(TESTDIR, "smallest")
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
