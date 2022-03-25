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
Unittest package init module.
"""

import atexit
import os
import shutil
import string
from datetime import datetime
from pathlib import Path

import pytest

from torrentfile.torrent import TorrentFile, TorrentFileHybrid, TorrentFileV2


def tempfile(path=None, exp=18):
    """Create temporary file.

    Creates a temporary file for unittesting purposes.py

    Parameters
    ----------
    path : str, optional
        relative path to temporary files, by default None
    exp : int, optional
        Exponent used to determine size of file., by default 18

    Returns
    -------
    str
        absolute path to file.
    """
    seq = (string.printable + string.whitespace).encode("utf-8")
    root = Path(__file__).parent / "TESTDIR"
    if not os.path.exists(root):
        os.mkdir(root)
    if not path:
        path = root / (str(datetime.timestamp(datetime.now())) + ".file")
    parts = Path(path).parts
    partial = root
    for i, part in enumerate(parts):
        partial = partial / part
        if i == len(parts) - 1:
            with open(partial, "wb") as binfile:
                size = 2**exp
                while size > 0:
                    if len(seq) < size:
                        binfile.write(seq)
                        size -= len(seq)
                        seq += seq
                    else:
                        binfile.write(seq[:size])
                        size -= size
        else:
            if not os.path.exists(partial):
                os.mkdir(partial)
    return partial


def rmpath(*args):
    """Remove file or directory path.

    Parameters
    ----------
    args : list
        Filesystem locations for removing.
    """
    for arg in args:
        if not os.path.exists(arg):
            continue
        if os.path.isdir(arg):
            try:
                shutil.rmtree(arg)
            except PermissionError:  # pragma: nocover
                pass
        elif os.path.isfile(arg):
            try:
                os.remove(arg)
            except PermissionError:  # pragma: nocover
                pass


def tempdir(ext="1"):
    """Create temporary directory.

    Parameters
    ----------
    ext : str, optional
        extension to file names, by default "1"

    Returns
    -------
    str
        path to common root for directory.
    """
    layouts = {
        "1": [
            f"dir{ext}/file1.png",
            f"dir{ext}/file2.mp4",
            f"dir{ext}/file3.mp3",
            f"dir{ext}/file4.zip",
        ],
        "2": [
            f"dir{ext}/file1.png",
            f"dir{ext}/subdir/file2.mp4",
            f"dir{ext}/subdir/file3.mp3",
            f"dir{ext}/subdir/subdir/file4.zip",
        ],
        "3": [
            f"dir{ext}/subdir1/file1.png",
            f"dir{ext}/subdir2/file2.mp4",
            f"dir{ext}/subdir2/file3.mp3",
            f"dir{ext}/subdir2/file4.zip",
        ],
        "4": [f"dir{ext}/file1.txt", f"dir{ext}/file2.rar"],
    }
    paths = []
    for path in layouts[ext]:
        temps = tempfile(path=path, exp=18)
        paths.append(temps)
    return os.path.commonpath(paths)


@atexit.register
def teardown():  # pragma: nocover
    """
    Remove all temporary directories and files.
    """
    root = Path(__file__).parent / "TESTDIR"
    for path in [root, "torrentfile.log"]:
        if os.path.exists(path):
            rmpath(path)


@pytest.fixture(scope="package")
def dir1():
    """Create a specific temporary structured directory.

    Yields
    ------
    str
        path to root of temporary directory
    """
    root = tempdir()
    yield root
    rmpath(root)


@pytest.fixture
def dir2():
    """Create a specific temporary structured directory.

    Yields
    ------
    str
        path to root of temporary directory
    """
    root = tempdir(ext="2")
    yield Path(root)
    rmpath(root)


def torrents():
    """
    Return seq of torrentfile objects.
    """
    return [TorrentFile, TorrentFileV2, TorrentFileHybrid]


@pytest.fixture(scope="package", params=torrents())
def metafile(request):
    """
    Create a standard metafile for testing.
    """
    root = tempdir(ext="4")
    args = {
        "path": root,
        "announce": ["url1", "url2", "url4"],
        "comment": "this is a comment",
        "source": "SomeSource",
        "private": 1,
    }
    torrent_class = request.param
    torrent = torrent_class(**args)
    outfile, _ = torrent.write()
    yield outfile
    rmpath(outfile, root)


@pytest.fixture
def tfile():
    """
    Return the path to a temporary file.
    """
    path = tempfile()
    yield path
    rmpath(path)
