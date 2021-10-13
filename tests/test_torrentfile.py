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

import pytest

from tests.context import rmpath, tempdir, tempfile
from torrentfile import TorrentFile
from torrentfile.utils import MissingPathError


@pytest.fixture(scope="module")
def tdir():
    """Return temporary directory."""
    folder = tempdir()
    args = {"path": folder, "announce": "https://tracker.com/announce"}
    yield (folder, args)
    rmpath(folder)


@pytest.fixture(scope="module")
def tfile():
    """Return temporary file."""
    fd = tempfile()
    args = {"path": fd, "announce": "https://tracker.com/announce"}
    yield (fd, args)
    rmpath(fd)


def test_torrentfile_dir(tdir):
    """Test temporary directory."""
    _, args = tdir
    torrent = TorrentFile(**args)
    assert torrent.meta is not None  # nosec


def test_torrentfile_file(tfile):
    """Test temporary file."""
    _, args = tfile
    torrent = TorrentFile(**args)
    assert torrent.meta is not None  # nosec


def test_torrentfile_file_private(tfile):
    """Test temporary file with arguments."""
    _, args = tfile
    args["private"] = True
    torrent = TorrentFile(**args)
    assert "private" in torrent.meta["info"]  # nosec


def test_torrentfile_dir_private(tdir):
    """Test temporary dir with arguments."""
    _, args = tdir
    args["private"] = True
    torrent = TorrentFile(**args)
    meta = torrent.meta
    assert "private" in meta["info"]  # nosec


def test_torrentfile_file_comment(tfile):
    """Test temporary file with arguments."""
    _, args = tfile
    args["private"] = True
    args["comment"] = "This is a comment"
    torrent = TorrentFile(**args)
    meta = torrent.meta
    assert "private" in meta["info"] and "comment" in meta["info"]  # nosec


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
