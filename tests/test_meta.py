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
from torrentfile.metafileV2 import TorrentFileV2
from torrentfile.metafile import TorrentFile, Checker
from tests.context import tempdir, tempfile, rmpaths


def maketorrent(args, v2=False):
    """Torrent making factory."""
    if v2:
        torrent = TorrentFileV2(**args)
    else:
        torrent = TorrentFile(**args)
    torrent.assemble()
    return torrent.write()


@pytest.fixture(scope="module")
def tdir():
    """Return temp directory."""
    return tempdir()


@pytest.fixture(scope="module")
def tfile():
    """Return temp file."""
    return tempfile()


@pytest.fixture(scope="module")
def metav2f(tfile):
    """Return generated metadata v2 for file."""
    args = {"private": True, "path": tfile, "announce": "http://announce.com/announce"}
    outfile, meta = maketorrent(args, v2=True)
    yield outfile, meta
    rmpaths([tfile, outfile])


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
    outfile, meta = maketorrent(args, v2=True)
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
def metav1f(tfile):
    """Return generated metadata v1 for file."""
    args = {"private": True, "path": tfile, "announce": "http://announce.com/announce"}
    outfile, meta = maketorrent(args)
    yield outfile, meta
    rmpaths([tfile, outfile])


@pytest.fixture(scope="module")
def tfilemeta(tfile):
    """Test metadata."""
    args = {"private": True, "path": tfile, "announce": "http://announce.com/announce"}
    outfile, _ = maketorrent(args)
    yield outfile, tfile
    rmpaths([tfile, outfile])


@pytest.fixture(scope="module")
def tdirmeta(tdir):
    """Test metadata."""
    args = {"private": True, "path": tdir, "announce": "http://announce.com/announce"}
    outfile, _ = maketorrent(args)
    yield outfile, tdir
    rmpaths([tdir, outfile])


def test_v2_meta_keys(metav2f):
    """Test metadata."""
    outfile, meta = metav2f
    for key in ["announce", "info", "piece layers", "creation date"]:
        assert key in meta
    assert os.path.exists(outfile)


def test_v2_info_keys_file(metav2f):
    """Test metadata."""
    outfile, meta = metav2f
    for key in [
        "length",
        "piece length",
        "meta version",
        "file tree",
        "name",
        "private",
    ]:
        assert key in meta["info"]
    assert os.path.exists(outfile)


def test_v2_info_keys_dir(metav2d):
    """Test metadata."""
    outfile, meta = metav2d
    for key in [
        "piece length",
        "meta version",
        "file tree",
        "name",
        "private",
        "source",
        "comment",
    ]:
        assert key in meta["info"]
    assert os.path.exists(outfile)


def test_v1_meta_keys(metav1f):
    """Test metadata."""
    outfile, meta = metav1f
    for key in ["announce", "info", "creation date"]:
        assert key in meta
    assert os.path.exists(outfile)


def test_v1_info_keys_file(metav1f):
    """Test metadata."""
    outfile, meta = metav1f
    for key in [
        "length",
        "piece length",
        "pieces",
        "name",
        "private",
    ]:
        assert key in meta["info"]
    assert os.path.exists(outfile)


def test_v1_info_keys_dir(metav1d):
    """Test metadata."""
    outfile, meta = metav1d
    for key in [
        "piece length",
        "pieces",
        "name",
        "private",
        "source",
        "comment",
    ]:
        assert key in meta["info"]
    assert os.path.exists(outfile)


def test_metafile_checker_v1_file(tfilemeta):
    """Test metadata."""
    outfile, tfile = tfilemeta
    checker = Checker(outfile, tfile)
    status = checker.check()
    assert status == "100%"


def test_metafile_checker_v1_dir(tdirmeta):
    """Test metadata."""
    outfile, tdir = tdirmeta
    checker = Checker(outfile, tdir)
    status = checker.check()
    assert status == "100%"
