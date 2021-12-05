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
"""Test main module functionality."""

import os
import sys

import pytest

from tests.context import Temp, rmpath, testfile
from torrentfile import TorrentFile, TorrentFileHybrid, TorrentFileV2
from torrentfile import main_script as main


@pytest.fixture(scope="module", params=list(range(14, 26)))
def tfile(request):
    """Create fixture for tests."""
    args = [
        "torrentfile",
        "--private",
        "--tracker",
        "https://tracker1.to/announce",
        "--source",
        "TFile",
    ]
    t_file = testfile(exp=request.param)
    yield args, t_file
    rmpath(t_file)


def test_main_func(tfile):
    """Test main script function."""
    args, path = tfile
    opath = os.path.join(Temp.root, "test.torrent")
    sys.argv = args + [path, "-o", opath]
    main()
    assert os.path.exists(opath)   # nosec
    rmpath(opath)


def test_main_announce_list(tfile):
    """Test main function with announce list flag."""
    args, path = tfile
    sys.argv = args + [
        path,
        "-t",
        "https://tracker2/announce",
        "https://tracker3/announce",
        "https://tracker4/announce",
    ]
    parser = main()
    url = "https://tracker4/announce"
    announce_list = parser.meta["announce list"]
    seq = [item for sub in announce_list for item in sub]
    assert url in seq  # nosec


def test_main_annlist_single(tfile):
    """Test main function with announce list flag."""
    args, path = tfile
    sys.argv = args + [
        "-t",
        "https://tracker2/announce",
    ]
    sys.argv.insert(1, path)
    parser = main()
    url = "https://tracker2/announce"
    announce_list = parser.meta["announce list"]
    seq = [item for sub in announce_list for item in sub]
    assert url in seq  # nosec


def test_class_with_annlist(tfile):
    """Test TorrentFile Class with announce list arguement."""
    _, path = tfile
    kwargs = {
        "path": path,
        "announce": (
            "https://tracker1.to/announce",
            "https://tracker2/announce",
            "https://tracker3/announce",
            "https://tracker4/announce",
        ),
    }
    torrent = TorrentFile(**kwargs)
    url = "https://tracker3/announce"
    announce_list = torrent.meta["announce list"]
    seq = [item for sub in announce_list for item in sub]
    assert url in seq  # nosec


def test_class_tuple_annlist(tfile):
    """Test TorrentFile Class with tuple announce list arguement."""
    _, path = tfile
    kwargs = {
        "path": path,
        "announce": (
            "https://tracker1.to/announce",
            "https://tracker2/announce",
            "https://tracker3/announce",
            "https://tracker4/announce",
        ),
    }
    torrent = TorrentFile(**kwargs)
    url = "https://tracker3/announce"
    announce_list = torrent.meta["announce list"]
    seq = [item for sub in announce_list for item in sub]
    assert url in seq  # nosec


def test_class_list_annlist(tfile):
    """Test TorrentFile Class with tuple announce list arguement."""
    _, path = tfile
    kwargs = {
        "path": path,
        "announce": [
            "https://tracker1.to/announce",
            "https://tracker2/announce",
            "https://tracker3/announce",
            "https://tracker4/announce",
        ],
    }
    torrent = TorrentFile(**kwargs)
    url = "https://tracker2/announce"
    announce_list = torrent.meta["announce list"]
    seq = [item for sub in announce_list for item in sub]
    assert url in seq  # nosec


def test_main_annlist_v2(tfile):
    """Test main function with announce list flag."""
    args, path = tfile
    sys.argv = args + [
        "-t",
        "https://tracker2/announce",
        "https://tracker3/announce",
        "https://tracker4/announce",
        "--meta-version",
        "2",
    ]
    sys.argv.insert(1, path)
    parser = main()
    url = "https://tracker2/announce"
    assert url in parser.meta["announce"]  # nosec
    rmpath(parser.outfile)


def test_main_annlist_v3(tfile):
    """Test main function with announce list flag."""
    args, path = tfile
    sys.argv = args + [
        "-t",
        "https://tracker2/announce",
        "https://tracker3/announce",
        "https://tracker4/announce",
        "--meta-version",
        "3",
    ]
    sys.argv.insert(1, path)
    parser = main()
    url = "https://tracker4/announce"
    announce_list = parser.meta["announce list"]
    seq = [item for sub in announce_list for item in sub]
    assert url in seq  # nosec


def test_main_annlist_single_v2(tfile):
    """Test main function with announce list flag."""
    args, path = tfile
    sys.argv = args + [
        "-t",
        "https://tracker2/announce",
        "--meta-version",
        "2",
    ]
    sys.argv.insert(1, path)
    parser = main()
    url = "https://tracker2/announce"
    assert url in parser.meta["announce"]  # nosec
    rmpath(parser.outfile)


def test_main_annlist_single_v3(tfile):
    """Test main function with announce list flag."""
    args, path = tfile
    sys.argv = args + [
        "-t",
        "https://tracker2/announce",
        "--meta-version",
        "3",
    ]
    sys.argv.insert(1, path)
    parser = main()
    url = "https://tracker2/announce"
    assert url in parser.meta["announce"]  # nosec
    rmpath(parser.outfile)


def test_main_annlist_single_v1(tfile):
    """Test main function with announce list flag."""
    args, path = tfile
    sys.argv = args + [
        "-t",
        "https://tracker2/announce",
        "--meta-version",
        "1",
    ]
    sys.argv.insert(1, path)
    parser = main()
    url = "https://tracker2/announce"
    assert url in parser.meta["announce"]  # nosec
    rmpath(parser.outfile)


def test_class_annlist_v2(tfile):
    """Test TorrentFile Class with announce list arguement."""
    _, path = tfile
    kwargs = {
        "path": path,
        "announce": (
            "https://tracker1.to/announce",
            "https://tracker2/announce",
            "https://tracker3/announce",
            "https://tracker4/announce",
        ),
    }
    torrent = TorrentFileV2(**kwargs)
    url = "https://tracker2/announce"
    announce_list = torrent.meta["announce list"]
    seq = [item for sub in announce_list for item in sub]
    assert url in seq  # nosec


def test_class_tuple_annlist_v2(tfile):
    """Test TorrentFile Class with tuple announce list arguement."""
    _, path = tfile
    kwargs = {
        "path": path,
        "announce": (
            "https://tracker1.to/announce",
            "https://tracker2/announce",
            "https://tracker3/announce",
            "https://tracker4/announce",
        ),
    }
    torrent = TorrentFileV2(**kwargs)
    url = "https://tracker2/announce"
    announce_list = torrent.meta["announce list"]
    seq = [item for sub in announce_list for item in sub]
    assert url in seq  # nosec


def test_class_list_annlist_v2(tfile):
    """Test TorrentFile Class with tuple announce list arguement."""
    _, path = tfile
    kwargs = {
        "path": path,
        "announce": [
            "https://tracker1.to/announce",
            "https://tracker2/announce",
            "https://tracker3/announce",
            "https://tracker4/announce",
        ],
    }
    torrent = TorrentFileV2(**kwargs)
    url = "https://tracker2/announce"
    announce_list = torrent.meta["announce list"]
    seq = [item for sub in announce_list for item in sub]
    assert url in seq  # nosec


@pytest.mark.parametrize("hasher", [TorrentFileV2, TorrentFileHybrid])
def test_class_single_file_small(hasher):
    """Test when single file is slightly larger than piece length."""
    path = testfile(exp=15)
    with open(path, "ab") as binfile:
        binfile.write((Temp.seq * 2).encode("utf-8"))
    args = {
        "path": path,
        "piece_length": 15,
        "source": "example1"
    }
    torrent = hasher(**args)
    tpath, _ = torrent.write()
    assert os.path.exists(tpath)   # nosec
