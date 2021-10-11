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
from torrentfile import TorrentFile, exceptions, utils


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
    data = torrent.assemble()
    assert data is not None  # nosec


def test_torrentfile_file(tfile):
    """Test temporary file."""
    _, args = tfile
    torrent = TorrentFile(**args)
    data = torrent.assemble()
    assert data is not None  # nosec


def test_torrentfile_file_private(tfile):
    """Test temporary file with arguments."""
    _, args = tfile
    args["private"] = True
    torrent = TorrentFile(**args)
    data = torrent.assemble()
    assert "private" in data["info"]  # nosec


def test_torrentfile_dir_private(tdir):
    """Test temporary dir with arguments."""
    _, args = tdir
    args["private"] = True
    torrent = TorrentFile(**args)
    data = torrent.assemble()
    assert "private" in data["info"]  # nosec


def test_torrentfile_file_comment(tfile):
    """Test temporary file with arguments."""
    _, args = tfile
    args["private"] = True
    args["comment"] = "This is a comment"
    torrent = TorrentFile(**args)
    data = torrent.assemble()
    assert "private" in data["info"] and "comment" in data["info"]  # nosec


def test_torrentfile_dir_comment(tdir):
    """Test temporary dir with arguments."""
    _, args = tdir
    args["private"] = True
    args["comment"] = "This is a comment"
    torrent = TorrentFile(**args)
    data = torrent.assemble()
    assert "private" in data["info"] and "comment" in data["info"]  # nosec


def test_exception_encoding_error():
    """Test temporary dir encoding with arguments."""
    try:
        val = set([1, 2, 3, 4, 5])
        encoder = utils.Benencoder()
        val = encoder.encode(val)
        assert False  # nosec
    except exceptions.BenencodingError:
        assert True  # nosec


def test_exception_decoding_error():
    """Test temporary dir decoding with arguments."""
    try:
        val = b"i:alphabet"
        decoder = utils.Bendecoder()
        val = decoder.decode(val)
        assert False  # nosec
    except exceptions.BendecodingError:
        assert True  # nosec


def test_exception_path_error():
    """Test MissingPathError exception."""
    try:
        raise exceptions.MissingPathError("this is a message")
    except exceptions.MissingPathError:
        assert True  # nosec
