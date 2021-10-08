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


import sys
import pytest
from tests.context import tempfile, rmpath
from torrentfile import TorrentFile, TorrentFileV2
from torrentfile import __main__ as entry
from torrentfile import main


@pytest.fixture(scope="module")
def tfile():
    """Create fixture for tests."""
    args = ["torrentfile",
            "--private",
            "--announce", "https://tracker1.to/announce",
            "--source", "TFile"]
    t_file = tempfile()
    yield args, t_file
    rmpath(t_file)


def test_main():
    """Test __maine__."""
    assert entry.__doc__


def test_main_with_announce_list(tfile):
    """Test main function with announce list flag."""
    args, path = tfile
    sys.argv = args + [
        "--path", path, "--announce-list", "https://tracker2/announce",
        "https://tracker3/announce", "https://tracker4/announce"
    ]
    parser = main()
    assert "https://tracker2/announce" in parser.meta["info"]["announce list"]
    rmpath(parser.outfile)


def test_main_with_announce_list_with_just_1_arg(tfile):
    """Test main function with announce list flag."""
    args, path = tfile
    sys.argv = args + [
        "--path", path, "--announce-list", "https://tracker2/announce"
    ]
    parser = main()
    assert "https://tracker2/announce" in parser.meta["info"]["announce list"]
    rmpath(parser.outfile)


def test_torrentfile_class_with_announce_list(tfile):
    """Test TorrentFile Class with announce list arguement."""
    _, path = tfile
    kwargs = {
        "announce": "https://tracker1.to/announce",
        "path": path,
        "announce_list": ("https://tracker2/announce"
                          " https://tracker3/announce"
                          " https://tracker4/announce")
    }
    torfile = TorrentFile(**kwargs)
    meta = torfile.assemble()
    assert "https://tracker2/announce" in meta["info"]["announce list"]


def test_torrentfile_class_with_tuple_announce_list(tfile):
    """Test TorrentFile Class with tuple announce list arguement."""
    _, path = tfile
    kwargs = {
        "announce": "https://tracker1.to/announce",
        "path": path,
        "announce_list": ("https://tracker2/announce",
                          "https://tracker3/announce",
                          "https://tracker4/announce")
    }
    torfile = TorrentFile(**kwargs)
    meta = torfile.assemble()
    assert "https://tracker2/announce" in meta["info"]["announce list"]


def test_torrentfile_class_with_list_announce_list(tfile):
    """Test TorrentFile Class with tuple announce list arguement."""
    _, path = tfile
    kwargs = {
        "announce": "https://tracker1.to/announce",
        "path": path,
        "announce_list": ["https://tracker2/announce",
                          "https://tracker3/announce",
                          "https://tracker4/announce"]
    }
    torfile = TorrentFile(**kwargs)
    meta = torfile.assemble()
    assert "https://tracker2/announce" in meta["info"]["announce list"]


def test_main_with_announce_list_v2(tfile):
    """Test main function with announce list flag."""
    args, path = tfile
    sys.argv = args + [
        "--path", path, "--announce-list", "https://tracker2/announce",
        "https://tracker3/announce", "https://tracker4/announce",
        "--meta-version", "2"
    ]
    parser = main()
    assert "https://tracker2/announce" in parser.meta["info"]["announce list"]
    rmpath(parser.outfile)


def test_main_with_announce_list_v3(tfile):
    """Test main function with announce list flag."""
    args, path = tfile
    sys.argv = args + [
        "--path", path, "--announce-list", "https://tracker2/announce",
        "https://tracker3/announce", "https://tracker4/announce",
        "--meta-version", "3"
    ]
    parser = main()
    assert "https://tracker2/announce" in parser.meta["info"]["announce list"]
    rmpath(parser.outfile)


def test_main_with_announce_list_with_just_1_arg_v2(tfile):
    """Test main function with announce list flag."""
    args, path = tfile
    sys.argv = args + [
        "--path", path, "--announce-list", "https://tracker2/announce", "--meta-version", "2"
    ]
    parser = main()
    assert "https://tracker2/announce" in parser.meta["info"]["announce list"]
    rmpath(parser.outfile)

def test_main_with_announce_list_with_just_1_arg_v3(tfile):
    """Test main function with announce list flag."""
    args, path = tfile
    sys.argv = args + [
        "--path", path, "--announce-list", "https://tracker2/announce", "--meta-version", "3"
    ]
    parser = main()
    assert "https://tracker2/announce" in parser.meta["info"]["announce list"]
    rmpath(parser.outfile)

def test_main_with_announce_list_with_just_1_arg_v1(tfile):
    """Test main function with announce list flag."""
    args, path = tfile
    sys.argv = args + [
        "--path", path, "--announce-list", "https://tracker2/announce", "--meta-version", "1"
    ]
    parser = main()
    assert "https://tracker2/announce" in parser.meta["info"]["announce list"]
    rmpath(parser.outfile)


def test_torrentfile_class_with_announce_list_v2(tfile):
    """Test TorrentFile Class with announce list arguement."""
    _, path = tfile
    kwargs = {
        "announce": "https://tracker1.to/announce",
        "path": path,
        "announce_list": ("https://tracker2/announce"
                          " https://tracker3/announce"
                          " https://tracker4/announce"),
    }
    torfile = TorrentFileV2(**kwargs)
    meta = torfile.assemble()
    assert "https://tracker2/announce" in meta["info"]["announce list"]


def test_torrentfile_class_with_tuple_announce_list_v2(tfile):
    """Test TorrentFile Class with tuple announce list arguement."""
    _, path = tfile
    kwargs = {
        "announce": "https://tracker1.to/announce",
        "path": path,
        "announce_list": ("https://tracker2/announce",
                          "https://tracker3/announce",
                          "https://tracker4/announce")
    }
    torfile = TorrentFileV2(**kwargs)
    meta = torfile.assemble()
    assert "https://tracker2/announce" in meta["info"]["announce list"]


def test_torrentfile_class_with_list_announce_list_v2(tfile):
    """Test TorrentFile Class with tuple announce list arguement."""
    _, path = tfile
    kwargs = {
        "announce": "https://tracker1.to/announce",
        "path": path,
        "announce_list": ["https://tracker2/announce",
                          "https://tracker3/announce",
                          "https://tracker4/announce"]
    }
    torfile = TorrentFileV2(**kwargs)
    meta = torfile.assemble()
    assert "https://tracker2/announce" in meta["info"]["announce list"]
