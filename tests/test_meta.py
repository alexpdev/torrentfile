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
"""Test metafile generators functionality."""

import os

import pytest

from tests.context import parameters, rmpaths
from torrentfile import utils
from torrentfile.metafile import Checker, TorrentFile
from torrentfile.metafile2 import TorrentFileV2


def maketorrent(args, ver2=False):
    """Torrent making factory."""
    if ver2:
        torrent = TorrentFileV2(**args)
    else:
        torrent = TorrentFile(**args)
    torrent.assemble()
    return torrent.write()


@pytest.fixture(scope="module", params=parameters())
def tdir(request):
    """Return temp directory."""
    return request.param()


@pytest.fixture(scope="module")
def metav2d(tdir):
    """Return generated metadata v2 for directory."""
    args = {
        "private": True,
        "path": tdir,
        "announce": "http://announce.com/announce",
        "source": "tracker",
        "comment": "content details and purpose",
    }
    outfile, meta = maketorrent(args, ver2=True)
    yield outfile, meta
    rmpaths([tdir, outfile])


@pytest.fixture(scope="module")
def metav1d(tdir):
    """Return generated metadata v1 for directory."""
    args = {
        "private": True,
        "path": tdir,
        "announce": "http://announce.com/announce",
        "source": "tracker",
        "comment": "content details and purpose",
    }
    outfile, meta = maketorrent(args)
    yield outfile, meta
    rmpaths([tdir, outfile])


@pytest.fixture(scope="module")
def tdirmeta(tdir):
    """Test metadata."""
    args = {
        "private": True,
        "path": tdir,
        "announce": "http://announce.com/announce",
    }
    outfile, _ = maketorrent(args)
    yield outfile, tdir
    rmpaths([tdir, outfile])


@pytest.mark.parametrize('key', ["announce", "info", "piece layers",
                                 "creation date", "created by"])
def test_v2_meta_keys(metav2d, key):
    """Test metadata."""
    outfile, meta = metav2d
    assert key in meta  # nosec
    assert os.path.exists(outfile)  # nosec


@pytest.mark.parametrize('key', ["piece length", "meta version", "file tree",
                                 "name", "private", "source", "comment"])
def test_v2_info_keys_dir(metav2d, key):
    """Test metadata."""
    outfile, meta = metav2d
    assert key in meta["info"]  # nosec
    assert os.path.exists(outfile)  # nosec


@pytest.mark.parametrize('key', ["announce", "info",
                                 "creation date", "created by"])
def test_v1_meta_keys(metav1d, key):
    """Test metadata."""
    outfile, meta = metav1d
    assert key in meta  # nosec
    assert os.path.exists(outfile)  # nosec


@pytest.mark.parametrize('key', ["piece length", "name", "private",
                                 "source", "comment", "pieces"])
def test_v1_info_keys_dir(metav1d, key):
    """Test metadata."""
    outfile, meta = metav1d
    assert key in meta["info"]  # nosec
    assert os.path.exists(outfile)  # nosec


def test_metafile_checker_v1_dir(tdirmeta):
    """Test metadata."""
    outfile, tdir = tdirmeta
    checker = Checker(outfile, tdir)
    status = checker.check()
    assert status == "100%"  # nosec


def test_meta_no_args_v2():
    """Test construct TorrentFileV2 with no arguments."""
    try:
        assert TorrentFileV2(private=True)   # nosec
    except utils.MissingPathError:
        assert True  # nosec


def test_meta_no_args_v1():
    """Test construct TorrentFile with no arguments."""
    try:
        assert TorrentFile(announce="url")   # nosec
    except utils.MissingPathError:
        assert True  # nosec
