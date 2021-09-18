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
from tests.context import tempfile, tempdir, rmpath


@pytest.fixture(scope="module")
def tdir():
    folder = tempdir()
    yield folder
    rmpath(folder)


@pytest.fixture(scope="module")
def tfile():
    fd = tempfile()
    yield fd
    rmpath(fd)


def test_torrentfile_dir(tdir):
    announce = "http://example.com/announce"
    torrent = TorrentFile(path=tdir, announce=announce, private=1)
    data = torrent.assemble()
    assert data is not None


def test_torrentfile_file(tfile):
    announce = "http://example.com/announce"
    torrent = TorrentFile(path=tfile, announce=announce, private=1)
    data = torrent.assemble()
    assert data is not None

