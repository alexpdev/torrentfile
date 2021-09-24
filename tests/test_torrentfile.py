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
from torrentfile import TorrentFile
from torrentfile import exceptions, utils
from tests.context import tempfile, tempdir, rmpath, Flags


@pytest.fixture(scope="module")
def flag():
    """Return meta flags."""
    def func(path):
        return Flags(**{"announce": "http://example.com/announce",
                        "path": path})
    return func


@pytest.fixture(scope="module")
def tdir(flag):
    """Return temporary directory."""
    folder = tempdir()
    flags = flag(folder)
    yield (folder, flags)
    rmpath(folder)


@pytest.fixture(scope="module")
def tfile(flag):
    """Return temporary file."""
    fd = tempfile()
    flags = flag(fd)
    yield (fd, flags)
    rmpath(fd)


def test_torrentfile_dir(tdir):
    """Test temporary directory."""
    _, flags = tdir
    torrent = TorrentFile(flags)
    data = torrent.assemble()
    assert data is not None


def test_torrentfile_file(tfile):
    """Test temporary file."""
    _, flags = tfile
    torrent = TorrentFile(flags)
    data = torrent.assemble()
    assert data is not None


def test_torrentfile_file_private(tfile):
    """Test temporary file with arguments."""
    _, flags = tfile
    flags.private = True
    torrent = TorrentFile(flags)
    data = torrent.assemble()
    assert "private" in data["info"]


def test_torrentfile_dir_private(tdir):
    """Test temporary dir with arguments."""
    _, flags = tdir
    flags.private = True
    torrent = TorrentFile(flags)
    data = torrent.assemble()
    assert "private" in data["info"]


def test_torrentfile_file_comment(tfile):
    """Test temporary file with arguments."""
    _, flags = tfile
    flags.private = True
    flags.comment = "This is a comment"
    torrent = TorrentFile(flags)
    data = torrent.assemble()
    assert "private" in data["info"] and "comment" in data["info"]


def test_torrentfile_dir_comment(tdir):
    """Test temporary dir with arguments."""
    _, flags = tdir
    flags.private = True
    flags.comment = "This is a comment"
    torrent = TorrentFile(flags)
    data = torrent.assemble()
    assert "private" in data["info"] and "comment" in data["info"]


def test_exception_encoding_error():
    """Test temporary dir encoding with arguments."""
    try:
        val = set([1, 2, 3, 4, 5])
        encoder = utils.Benencoder()
        val = encoder.encode(val)
        assert False
    except exceptions.BenencodingError:
        assert True


def test_exception_decoding_error():
    """Test temporary dir decoding with arguments."""
    try:
        val = b'i:alphabet'
        decoder = utils.Bendecoder()
        val = decoder.decode(val)
        assert False
    except exceptions.BendecodingError:
        assert True


def test_exception_missing_path_error():
    """Test MissingPathError exception."""
    try:
        raise exceptions.MissingPathError("this is a message")
    except exceptions.MissingPathError:
        assert True
