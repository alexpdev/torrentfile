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
"""
Testing functions for the command line interface.
"""

import os
import sys

import pyben
import pytest

from tests import rmpath, torrents
from torrentfile.cli import main
from torrentfile.interactive import select_action
from torrentfile.utils import normalize_piece_length

MOCK = "torrentfile.interactive.get_input"


@pytest.fixture
def testfile():
    """
    Create temporary file for unit tests.
    """
    parent = os.path.dirname(__file__)
    testdir = os.path.join(parent, "ITDIR")
    if not os.path.exists(testdir):
        os.mkdir(testdir)
    filename = os.path.join(testdir, "file123.dat")
    with open(filename, "wb") as tfile:
        sample = b"1234509876" * 37123
        tfile.write(sample)
    return filename


@pytest.fixture(params=torrents())
def metafile(testfile, request):
    """
    Fixture providing a torrent meta file for testing.
    """
    args = {
        "piece_length": 16,
        "announce": ["url1", "url2"],
        "private": 1,
        "comment": "Some comment here",
        "source": "SomeTrackerSource",
        "path": testfile,
        "outfile": str(testfile) + ".torrent",
    }
    torrent = request.param(**args)
    metafile, _ = torrent.write()
    yield metafile
    parent = os.path.dirname(testfile)
    rmpath(parent)


def test_interactive_create(monkeypatch, testfile):
    """
    Test creating torrent interactively.
    """
    mapping = [
        "create",
        "",
        "",
        "",
        "",
        "",
        "",
        testfile,
        str(testfile) + ".torrent",
        "",
    ]
    it = iter(mapping)
    monkeypatch.setattr(MOCK, lambda *_: next(it))
    select_action()
    assert os.path.exists(testfile + ".torrent")
    parent = os.path.dirname(testfile)
    rmpath(parent)


@pytest.mark.parametrize("version", ["1", "2", "3"])
@pytest.mark.parametrize("piece_length", ["23", "18", "131072"])
@pytest.mark.parametrize("announce", ["url1", "urla urlb urlc"])
@pytest.mark.parametrize("url_list", ["ftp url2", "ftp1 ftp2 ftp3"])
@pytest.mark.parametrize("comment", ["Some Comment", "No Comment"])
@pytest.mark.parametrize("source", ["Do", "Ra", "Me"])
def test_inter_create_full(
    testfile,
    piece_length,
    announce,
    comment,
    source,
    url_list,
    version,
    monkeypatch,
):
    """
    Test creating torrent interactively with many parameters.
    """
    mapping = [
        "create",
        piece_length,
        announce,
        url_list,
        comment,
        source,
        "Y",
        testfile,
        str(testfile) + ".torrent",
        version,
    ]
    it = iter(mapping)
    monkeypatch.setattr(MOCK, lambda *_: next(it))
    select_action()
    meta = pyben.load(str(testfile) + ".torrent")
    assert meta["info"]["source"] == source
    assert meta["info"]["piece length"] == normalize_piece_length(piece_length)
    assert meta["info"]["comment"] == comment
    assert meta["url-list"] == url_list.split()
    parent = os.path.dirname(testfile)
    rmpath(parent)


@pytest.mark.parametrize("announce", ["url1"])
@pytest.mark.parametrize("url_list", ["ftp url2", "ftp1 ftp2 ftp3"])
@pytest.mark.parametrize("comment", ["Some Comment", "No Comment"])
@pytest.mark.parametrize("source", ["Fa", "So", "La"])
def test_inter_edit_full(
    metafile, announce, comment, source, url_list, monkeypatch
):
    """
    Test editing torrent file interactively.
    """
    seq = [
        "edit",
        metafile,
        "4",
        announce,
        "1",
        comment,
        "2",
        source,
        "5",
        url_list,
        "6",
        "Y",
        "DONE",
    ]
    it = iter(seq)
    monkeypatch.setattr(MOCK, lambda *_: next(it))
    select_action()
    meta1 = pyben.load(metafile)
    assert meta1["info"]["source"] == source
    assert meta1["info"]["comment"] == comment
    assert meta1["url-list"] == url_list.split()
    assert meta1["info"]["private"] == 1


@pytest.mark.parametrize("announce", ["urla urlb urlc", "urld url2"])
@pytest.mark.parametrize("url_list", ["ftp url2", "ftp1 ftp2 ftp3"])
@pytest.mark.parametrize("comment", ["Some Comment"])
@pytest.mark.parametrize("source", ["Do", "Ra"])
def test_inter_edit_cli(
    metafile, announce, comment, source, url_list, monkeypatch
):
    """
    Test editing torrent interactively from CLI.
    """
    seq = [
        "edit",
        metafile,
        "4",
        announce,
        "1",
        comment,
        "2",
        source,
        "5",
        url_list,
        "6",
        "Y",
        "DONE",
    ]
    it = iter(seq)
    monkeypatch.setattr(MOCK, lambda *_: next(it))
    sys.argv = ["torrentfile", "-i"]
    main()
    meta2 = pyben.load(metafile)
    assert meta2["info"]["source"] == source
    assert meta2["info"]["comment"] == comment
    assert meta2["url-list"] == url_list.split()
    assert meta2["info"]["private"] == 1


@pytest.mark.parametrize("torrentclass", torrents())
def test_inter_recheck(torrentclass, monkeypatch, testfile):
    """
    Test interactive recheck function.
    """
    torrent = torrentclass(path=testfile)
    metafile, _ = torrent.write()
    seq = ["recheck", metafile, str(testfile)]
    it = iter(seq)
    monkeypatch.setattr(MOCK, lambda *_: next(it))
    result = select_action()
    assert result == 100
    parent = os.path.dirname(testfile)
    rmpath(parent)
