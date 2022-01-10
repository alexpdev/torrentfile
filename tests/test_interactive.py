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
"""Testing functions for the command line interface."""

import os
import sys

import pyben
import pytest

import torrentfile
from tests import dir1, dir2, rmpath, tempfile
from torrentfile.cli import main
from torrentfile.interactive import select_action
from torrentfile.torrent import TorrentFile, TorrentFileHybrid, TorrentFileV2
from torrentfile.utils import normalize_piece_length


def torrents():
    """Return all versions of TorrentFile objects."""
    return [TorrentFile, TorrentFileV2, TorrentFileHybrid]


def input_mapping(mapping):
    """Alternative input caturer."""

    def get_input(msg, _=None):
        """Get user input."""
        for key, val in mapping.items():
            if key in msg:
                return val
        return ""

    torrentfile.interactive.get_input = get_input


def test_fixtures():
    """Test dir1 and dir2 fixtures."""
    assert dir1 and dir2


def input_iter(seq):
    """Alternative input capture from sequence."""
    iterator = iter(seq)

    def get_input(_, func=None):
        """Get user input from iterator."""
        _ = func
        return next(iterator)

    torrentfile.interactive.get_input = get_input


@pytest.fixture(params=torrents())
def metafile(dir2, request):
    """Fixture providing a torrent meta file for testing."""
    args = {
        "piece_length": 16,
        "announce": ["url1", "url2"],
        "private": 1,
        "comment": "Some comment here",
        "source": "SomeTrackerSource",
        "path": dir2,
        "outfile": str(dir2) + ".torrent",
    }
    torrent = request.param(**args)
    metafile, _ = torrent.write()
    yield metafile
    rmpath(metafile)


def test_interactive_create(dir1):
    """Test creating torrent interactively."""
    mapping = {
        "Action": "create",
        "Content": dir1,
        "Output": str(dir1) + ".torrent",
    }
    input_mapping(mapping)
    select_action()
    assert os.path.exists(dir1 + ".torrent")


@pytest.mark.parametrize("version", ["1", "2", "3"])
@pytest.mark.parametrize("piece_length", ["23", "18", "131072"])
@pytest.mark.parametrize("announce", ["url1", "urla urlb urlc"])
@pytest.mark.parametrize("url_list", ["ftp url2", "ftp1 ftp2 ftp3"])
@pytest.mark.parametrize("comment", ["Some Comment", "No Comment"])
@pytest.mark.parametrize("source", ["Do", "Ra", "Me"])
def test_inter_create_full(
    dir1, piece_length, announce, comment, source, url_list, version
):
    """Test creating torrent interactively with many parameters."""
    mapping = {
        "Action": "create",
        "Content": dir1,
        "Piece": piece_length,
        "Tracker": announce,
        "Comment": comment,
        "Source": source,
        "Web": url_list,
        "Private": "Y",
        "Meta": version,
    }
    input_mapping(mapping)
    select_action()
    meta = pyben.load(dir1 + ".torrent")
    assert meta["info"]["source"] == source
    assert meta["info"]["piece length"] == normalize_piece_length(piece_length)
    assert meta["info"]["comment"] == comment
    assert meta["url-list"] == url_list.split()


@pytest.mark.parametrize("announce", ["url1"])
@pytest.mark.parametrize("url_list", ["ftp url2", "ftp1 ftp2 ftp3"])
@pytest.mark.parametrize("comment", ["Some Comment", "No Comment"])
@pytest.mark.parametrize("source", ["Fa", "So", "La"])
def test_inter_edit_full(metafile, announce, comment, source, url_list):
    """Test editing torrent file interactively."""
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
    input_iter(seq)
    select_action()
    meta = pyben.load(metafile)
    assert meta["info"]["source"] == source
    assert meta["info"]["comment"] == comment
    assert meta["url-list"] == url_list.split()
    assert meta["info"]["private"] == 1


@pytest.mark.parametrize("announce", ["urla urlb urlc", "urld url2"])
@pytest.mark.parametrize("url_list", ["ftp url2", "ftp1 ftp2 ftp3"])
@pytest.mark.parametrize("comment", ["Some Comment"])
@pytest.mark.parametrize("source", ["Do", "Ra"])
def test_inter_edit_cli(metafile, announce, comment, source, url_list):
    """Test editing torrent interactively from CLI."""
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
    input_iter(seq)
    sys.argv = ["torrentfile", "-i"]
    main()
    meta = pyben.load(metafile)
    assert meta["info"]["source"] == source
    assert meta["info"]["comment"] == comment
    assert meta["url-list"] == url_list.split()
    assert meta["info"]["private"] == 1


@pytest.mark.parametrize("size", list(range(16, 22)))
@pytest.mark.parametrize("torrentclass", torrents())
def test_inter_recheck(size, torrentclass):
    """Test interactive recheck function."""
    tfile = tempfile(exp=size)
    torrent = torrentclass(path=tfile)
    metafile, _ = torrent.write()
    seq = ["recheck", metafile, str(tfile)]
    input_iter(seq)
    result = select_action()
    assert result == 100
