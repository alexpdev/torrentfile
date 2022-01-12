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

import datetime
import os
import sys

import pyben
import pytest

from tests import dir1, dir2, rmpath
from torrentfile.cli import main


def test_cli_v1(dir1):
    """Basic create torrent cli command."""
    args = ["torrentfile", "create", str(dir1)]
    sys.argv = args
    main()
    assert os.path.exists(str(dir1) + ".torrent")
    rmpath(str(dir1) + ".torrent")


def test_cli_v2(dir1):
    """Create torrent v2 cli command."""
    args = ["torrentfile", "create", str(dir1), "--meta-version", "2"]
    sys.argv = args
    main()
    assert os.path.exists(str(dir1) + ".torrent")
    rmpath(str(dir1) + ".torrent")


def test_cli_v3(dir1):
    """Create hybrid torrent cli command."""
    args = ["torrentfile", "create", str(dir1), "--meta-version", "3"]
    sys.argv = args
    main()
    assert os.path.exists(str(dir1) + ".torrent")
    rmpath(str(dir1) + ".torrent")


def test_cli_private(dir1):
    """Test private cli flag."""
    args = ["torrentfile", "create", str(dir1), "--private"]
    sys.argv = args
    main()
    meta = pyben.load(str(dir1) + ".torrent")
    assert "private" in meta["info"]
    rmpath(str(dir1) + ".torrent")


@pytest.mark.parametrize("piece_length", [2 ** exp for exp in range(14, 21)])
@pytest.mark.parametrize("version", ["1", "2", "3"])
def test_cli_piece_length(dir1, piece_length, version):
    """Test piece length cli flag."""
    args = [
        "torrentfile",
        "-v",
        "create",
        str(dir1),
        "--piece-length",
        str(piece_length),
        "--meta-version",
        version,
        "--progress"
    ]
    sys.argv = args
    main()
    meta = pyben.load(str(dir1) + ".torrent")
    assert meta["info"]["piece length"] == piece_length
    rmpath(str(dir1) + ".torrent")


@pytest.mark.parametrize("piece_length", [2 ** exp for exp in range(14, 21)])
@pytest.mark.parametrize("version", ["1", "2", "3"])
def test_cli_announce(dir1, piece_length, version):
    """Test announce cli flag."""
    args = [
        "torrentfile",
        "create",
        str(dir1),
        "--piece-length",
        str(piece_length),
        "--meta-version",
        version,
        "--tracker",
        "https://announce.org/tracker",
    ]
    sys.argv = args
    main()
    meta = pyben.load(str(dir1) + ".torrent")
    assert meta["announce"] == "https://announce.org/tracker"
    rmpath(str(dir1) + ".torrent")


@pytest.mark.parametrize("version", ["1", "2", "3"])
def test_cli_announce_list(dir1, version):
    """Test announce-list cli flag."""
    trackers = [
        "https://announce.org/tracker",
        "https://announce.net/tracker",
        "https://tracker.net/announce",
    ]
    args = [
        "torrentfile",
        "create",
        str(dir1),
        "--meta-version",
        version,
        "--tracker",
    ] + trackers
    sys.argv = args
    main()
    meta = pyben.load(str(dir1) + ".torrent")
    for url in trackers:
        assert url in [j for i in meta["announce-list"] for j in i]
    rmpath(str(dir1) + ".torrent")


@pytest.mark.parametrize("piece_length", [2 ** exp for exp in range(14, 21)])
@pytest.mark.parametrize("version", ["1", "2", "3"])
def test_cli_comment(dir1, piece_length, version):
    """Test comment cli flag."""
    args = [
        "torrentfile",
        "create",
        str(dir1),
        "--piece-length",
        str(piece_length),
        "--meta-version",
        version,
        "--magnet",
        "--comment",
        "this is a comment",
    ]
    sys.argv = args
    main()
    meta = pyben.load(str(dir1) + ".torrent")
    assert meta["info"]["comment"] == "this is a comment"
    rmpath(str(dir1) + ".torrent")


@pytest.mark.parametrize("piece_length", [2 ** exp for exp in range(14, 21)])
@pytest.mark.parametrize("version", ["1", "2", "3"])
def test_cli_outfile(dir1, piece_length, version):
    """Test outfile cli flag."""
    outfile = str(dir1) + "test.torrent"
    args = [
        "torrentfile",
        "create",
        str(dir1),
        "--piece-length",
        str(piece_length),
        "--meta-version",
        version,
        "-o",
        outfile,
    ]
    sys.argv = args
    main()
    assert os.path.exists(outfile)
    rmpath(outfile)


@pytest.mark.parametrize("piece_length", [2 ** exp for exp in range(14, 21)])
@pytest.mark.parametrize("version", ["1", "2", "3"])
def test_cli_creation_date(dir1, piece_length, version):
    """Test if torrents created get an accurate timestamp."""
    args = [
        "torrentfile",
        "create",
        str(dir1),
        "--piece-length",
        str(piece_length),
        "--meta-version",
        version,
        "--comment",
        "this is a comment",
    ]
    sys.argv = args
    main()
    meta = pyben.load(str(dir1) + ".torrent")
    num = float(meta["creation date"])
    date = datetime.datetime.fromtimestamp(num)
    now = datetime.datetime.now()
    assert date.day == now.day
    assert date.year == now.year
    assert date.month == now.month
    rmpath(str(dir1) + ".torrent")


@pytest.mark.parametrize("piece_length", [2 ** exp for exp in range(14, 21)])
@pytest.mark.parametrize("version", ["1", "2", "3"])
def test_cli_created_by(dir1, piece_length, version):
    """Test if created torrents recieve a created by field in meta info."""
    args = [
        "torrentfile",
        "create",
        str(dir1),
        "--piece-length",
        str(piece_length),
        "--meta-version",
        version,
        "--comment",
        "this is a comment",
    ]
    sys.argv = args
    main()
    meta = pyben.load(str(dir1) + ".torrent")
    assert "TorrentFile" in meta["created by"]
    rmpath(str(dir1) + ".torrent")


@pytest.mark.parametrize("piece_length", [2 ** exp for exp in range(14, 21)])
@pytest.mark.parametrize("version", ["1", "2", "3"])
def test_cli_web_seeds(dir1, piece_length, version):
    """Test if created torrents recieve a created by field in meta info."""
    args = [
        "torrentfile",
        "create",
        str(dir1),
        "--piece-length",
        str(piece_length),
        "--meta-version",
        version,
        "-w",
        "https://webseed.url/1",
        "https://webseed.url/2",
        "https://webseed.url/3",
    ]
    sys.argv = args
    main()
    meta = pyben.load(str(dir1) + ".torrent")
    assert "https://webseed.url/1" in meta["url-list"]
    rmpath(str(dir1) + ".torrent")


@pytest.mark.parametrize("piece_length", [2 ** exp for exp in range(14, 21)])
@pytest.mark.parametrize("version", ["1", "2", "3"])
def test_cli_with_debug(dir1, piece_length, version):
    """Test debug mode cli flag."""
    args = [
        "torrentfile",
        "-v",
        "create",
        str(dir1),
        "--piece-length",
        str(piece_length),
        "--meta-version",
        version,
        "--comment",
        "this is a comment",
    ]
    sys.argv = args
    main()
    assert os.path.exists(str(dir1) + ".torrent")
    rmpath(str(dir1) + ".torrent")


@pytest.mark.parametrize("piece_length", [2 ** exp for exp in range(14, 21)])
@pytest.mark.parametrize("version", ["1", "2", "3"])
def test_cli_with_source(dir1, piece_length, version):
    """Test source cli flag."""
    args = [
        "torrentfile",
        "create",
        str(dir1),
        "--piece-length",
        str(piece_length),
        "--meta-version",
        version,
        "--source",
        "somesource",
    ]
    sys.argv = args
    main()
    meta = pyben.load(str(dir1) + ".torrent")
    assert meta["info"]["source"] == "somesource"
    rmpath(str(dir1) + ".torrent")


def test_cli_help():
    """Test showing help notice cli flag."""
    args = ["-h"]
    sys.argv = args
    try:
        assert main()
    except SystemExit:
        assert True
        assert dir1
        assert dir2


@pytest.mark.parametrize("version", ["1", "2", "3"])
@pytest.mark.parametrize("progress", [True, False])
def test_cli_empty_files(dir2, version, progress):
    """Test creating torrent with empty files."""
    args = [
        "torrentfile",
        "create",
        str(dir2),
        "--meta-version",
        version,
        "--source",
        "somesource",
    ]
    sys.argv = args
    if progress:
        sys.argv.append("--progress")

    def walk(root, count):
        """Traverse directory to edit files."""
        if root.is_file():
            with open(root, "wb") as _:
                return 1
        elif root.is_dir():
            for item in root.iterdir():
                if count >= 2:
                    break
                count += walk(item, count)
        return count

    walk(dir2, 0)
    main()
    assert os.path.exists(str(dir2) + ".torrent")
    rmpath(str(dir2) + ".torrent")
