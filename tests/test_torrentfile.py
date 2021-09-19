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

import pytest
from torrentfile import TorrentFile
from tests.context import tempfile, tempdir, rmpath, Flags


@pytest.fixture(scope="module")
def flag():
    def func(path):
        return Flags(**{"announce": "http://example.com/announce",
                        "path": path})
    return func


@pytest.fixture(scope="module")
def tdir(flag):
    folder = tempdir()
    flags = flag(folder)
    yield (folder, flags)
    rmpath(folder)


@pytest.fixture(scope="module")
def tfile(flag):
    fd = tempfile()
    flags = flag(fd)
    yield (fd, flags)
    rmpath(fd)


def test_torrentfile_dir(tdir):
    _, flags = tdir
    torrent = TorrentFile(flags)
    data = torrent.assemble()
    assert data is not None


def test_torrentfile_file(tfile):
    _, flags = tfile
    torrent = TorrentFile(flags)
    data = torrent.assemble()
    assert data is not None

def test_torrentfile_file_private(tfile):
    _, flags = tfile
    flags.private = True
    torrent = TorrentFile(flags)
    data = torrent.assemble()
    assert "private" in data["info"]

def test_torrentfile_dir_private(tdir):
    _, flags = tdir
    flags.private = True
    torrent = TorrentFile(flags)
    data = torrent.assemble()
    assert "private" in data["info"]

def test_torrentfile_file_comment(tfile):
    _, flags = tfile
    flags.private = True
    flags.comment = "This is a comment"
    torrent = TorrentFile(flags)
    data = torrent.assemble()
    assert "private" in data["info"] and "comment" in data["info"]

def test_torrentfile_dir_comment(tdir):
    _, flags = tdir
    flags.private = True
    flags.comment = "This is a comment"
    torrent = TorrentFile(flags)
    data = torrent.assemble()
    assert "private" in data["info"] and "comment" in data["info"]
