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
"""Testing the edit torrent feature."""

import sys

import pyben
import pytest

from tests import dir2, rmpath
from torrentfile.cli import main
from torrentfile.edit import edit_torrent
from torrentfile.torrent import TorrentFile, TorrentFileHybrid, TorrentFileV2


def torrents():
    """Return seq of torrentfile objects."""
    return [TorrentFile, TorrentFileV2, TorrentFileHybrid]


@pytest.fixture(scope="function", params=torrents())
def torfile(dir2, request):
    """Create a standard metafile for testing."""
    args = {
        "path": dir2,
        "announce": "url1 url2 url4",
        "comment": "this is a comment",
        "source": "SomeSource",
    }
    torrent_class = request.param
    torrent = torrent_class(**args)
    outfile, _ = torrent.write()
    yield outfile
    rmpath(outfile)


def test_fix():
    """Testing dir fixtures."""
    assert dir2


@pytest.mark.parametrize(
    "announce", [["urla"], ["urlb", "urlc"], ["urla", "urlb", "urlc"]]
)
def test_edit_torrent(torfile, announce):
    """Test edit torrent with announce param."""
    edits = {"announce": announce}
    data = edit_torrent(torfile, edits)
    meta = pyben.load(torfile)
    assert data == meta
    assert data["announce list"] == [announce]


@pytest.mark.parametrize("announce", ["urla", "urlb urlc", "urla urlb urlc"])
def test_edit_torrent_str(torfile, announce):
    """Test edit torrent with announce param as string."""
    edits = {"announce": announce}
    data = edit_torrent(torfile, edits)
    meta = pyben.load(torfile)
    assert data == meta
    assert data["announce list"] == [announce.split()]


@pytest.mark.parametrize("url_list", ["urla", "urlb urlc", "urla urlb urlc"])
def test_edit_urllist_str(torfile, url_list):
    """Test edit torrent with webseed param."""
    edits = {"url-list": url_list}
    data = edit_torrent(torfile, edits)
    meta = pyben.load(torfile)
    assert data == meta
    assert data["url-list"] == url_list.split()


@pytest.mark.parametrize(
    "url_list", [["urla"], ["urlb", "urlc"], ["urla", "urlb", "urlc"]]
)
def test_edit_urllist(torfile, url_list):
    """Test edit torrent with webseed param as string."""
    edits = {"url-list": url_list}
    data = edit_torrent(torfile, edits)
    meta = pyben.load(torfile)
    assert data == meta
    assert data["url-list"] == url_list


@pytest.mark.parametrize("comment", ["COMMENT", "COMIT", "MITCO"])
def test_edit_comment(torfile, comment):
    """Test edit torrent with comment param."""
    edits = {"comment": comment}
    data = edit_torrent(torfile, edits)
    meta = pyben.load(torfile)
    assert data == meta
    assert data["info"]["comment"] == comment


@pytest.mark.parametrize("source", ["SomeSource", "NoSouce", "MidSource"])
def test_edit_source(torfile, source):
    """Test edit torrent with source param."""
    edits = {"source": source}
    data = edit_torrent(torfile, edits)
    meta = pyben.load(torfile)
    assert data == meta
    assert data["info"]["source"] == source


def test_edit_private_true(torfile):
    """Test edit torrent with private param."""
    edits = {"private": "1"}
    data = edit_torrent(torfile, edits)
    meta = pyben.load(torfile)
    assert data == meta
    assert data["info"]["private"] == 1


def test_edit_private_false(torfile):
    """Test edit torrent with private param False."""
    edits = {"private": ""}
    data = edit_torrent(torfile, edits)
    meta = pyben.load(torfile)
    assert data == meta
    assert "private" not in data["info"]


def test_edit_none(torfile):
    """Test edit torrent with None for all params."""
    edits = {
        "announce": None,
        "url-list": None,
        "comment": None,
        "source": None,
        "private": None,
    }
    data = pyben.load(torfile)
    edited = edit_torrent(torfile, edits)
    meta = pyben.load(torfile)
    assert data == meta == edited


def test_edit_removal(torfile):
    """Test edit torrent with empty for all params."""
    edits = {
        "announce": "",
        "url-list": "",
        "comment": "",
        "source": "",
        "private": "",
    }
    data = edit_torrent(torfile, edits)
    meta = pyben.load(torfile)
    assert data == meta


@pytest.mark.parametrize("comment", ["commenta", "commentb", "commentc"])
@pytest.mark.parametrize("source", ["sourcea", "sourceb", "sourcec"])
@pytest.mark.parametrize("announce", [["url1", "url2", "url3"], ["url1"]])
@pytest.mark.parametrize("webseed", [["ftp1"], ["ftpa", "ftpb"]])
def test_edit_cli(torfile, comment, source, announce, webseed):
    """Test edit torrent with all params on cli."""
    sys.argv = [
        "torrentfile",
        "edit",
        torfile,
        "--comment",
        comment,
        "--source",
        source,
        "--web-seed",
        webseed,
        "--tracker",
        announce,
        "--private",
    ]
    main()
    meta = pyben.load(torfile)
    info = meta["info"]
    assert comment == info.get("comment")
    assert source == info.get("source")
    assert info.get("private") == 1
    assert meta["announce list"] == [[announce]]
    assert meta["url-list"] == [webseed]
