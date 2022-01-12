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
"""Testing functions for the torrent module."""
import os

import pytest

from tests import dir1, dir2, rmpath, tempfile
from torrentfile.torrent import (MetaFile, TorrentFile, TorrentFileHybrid,
                                 TorrentFileV2)
from torrentfile.utils import MissingPathError


def torrents():
    """Return a list of classes for creating torrents."""
    return [TorrentFile, TorrentFileV2, TorrentFileHybrid]


def test_fixtures():
    """Test pytest fixtures."""
    assert dir1 and dir2


@pytest.mark.parametrize("version", torrents())
def test_torrentfile_missing_path(version):
    """Test missing path error exception."""
    try:
        version()
    except MissingPathError:
        assert True


def test_metafile_assemble(dir1):
    """Test assembling base metafile exception."""
    metafile = MetaFile(path=dir1)
    try:
        metafile.assemble()
    except NotImplementedError:
        assert True


@pytest.mark.parametrize("version", torrents())
def test_torrentfile_extra(dir2, version):
    """Test creating a torrent meta file with given directory plus extra."""

    def walk(item):
        """Edit files in directory structure."""
        if item.is_file():
            with open(item, "ab") as binfile:
                binfile.write(bytes(1000))
        elif item.is_dir():
            for sub in item.iterdir():
                walk(sub)

    walk(dir2)
    args = {
        "path": dir2,
        "comment": "somecomment",
        "announce": "announce",
        "progress": True,
    }
    torrent = version(**args)
    assert torrent.meta["announce"] == "announce"


@pytest.mark.parametrize("size", list(range(17, 25)))
@pytest.mark.parametrize("piece_length", [2 ** i for i in range(14, 18)])
@pytest.mark.parametrize("version", torrents())
@pytest.mark.parametrize("progress", [True, False])
def test_torrentfile_single(version, size, piece_length, progress, capsys):
    """Test creating a torrent file from a single file contents."""
    tfile = tempfile(exp=size)
    with capsys.disabled():
        version.set_callback(print)
    args = {
        "path": tfile,
        "comment": "somecomment",
        "announce": "announce",
        "piece_length": piece_length,
        "progress": progress,
    }
    trent = version(**args)
    trent.write()
    assert os.path.exists(str(tfile) + ".torrent")
    rmpath(tfile, str(tfile) + ".torrent")


@pytest.mark.parametrize("size", list(range(17, 25)))
@pytest.mark.parametrize("piece_length", [2 ** i for i in range(14, 18)])
@pytest.mark.parametrize("version", torrents())
def test_torrentfile_single_extra(version, size, piece_length):
    """Test creating a torrent file from a single file contents plus extra."""
    tfile = tempfile(exp=size)
    with open(tfile, "ab") as binfile:
        binfile.write(bytes(str(tfile).encode("utf-8")))
    args = {
        "path": tfile,
        "comment": "somecomment",
        "announce": "announce",
        "piece_length": piece_length,
    }
    torrent = version(**args)
    torrent.write()
    outfile = str(tfile) + ".torrent"
    assert os.path.exists(outfile)
    rmpath(tfile, outfile)


@pytest.mark.parametrize("size", list(range(17, 25)))
@pytest.mark.parametrize("piece_length", [2 ** i for i in range(14, 18)])
@pytest.mark.parametrize("version", torrents())
def test_torrentfile_single_under(version, size, piece_length):
    """Test creating a torrent file from less than a single file contents."""
    tfile = tempfile(exp=size)
    with open(tfile, "rb") as binfile:
        data = binfile.read()
    with open(tfile, "wb") as binfile:
        binfile.write(data[: -(2 ** 9)])
    kwargs = {
        "path": tfile,
        "comment": "somecomment",
        "announce": "announce",
        "piece_length": piece_length,
    }
    torrent = version(**kwargs)
    outfile, _ = torrent.write()
    assert os.path.exists(outfile)
    rmpath(tfile, outfile)
