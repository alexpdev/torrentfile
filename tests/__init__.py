#! /usr/bin/python3
# -*- coding: utf-8 -*-

##############################################################################
#    Copyright (C) 2021-current alexpdev
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
##############################################################################
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

from torrentfile.torrent import (
    TorrentAssembler,
    TorrentFile,
    TorrentFileHybrid,
    TorrentFileV2,
)


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
    *args : list
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
            f"dir{ext}/file5.txt",
            f"dir{ext}/subdir1/subdir2/file.7z",
            f"dir{ext}/subdir/subdir/file4.rar",
            f"dir{ext}/subdir/subdir/file4.r01",
        ],
        "2": [
            f"dir{ext}/file1.png",
            f"dir{ext}/file2.jpg",
            f"dir{ext}/subdir/file2.mp4",
            f"dir{ext}/subdir/file3.mp3",
        ],
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
    dest = Path(__file__).parent / "dest"
    dest2 = Path(__file__).parent / "dest2"
    for path in [root, "./torrentfile.log", dest, dest2]:
        if os.path.exists(path):
            rmpath(path)


def torrents():
    """
    Return seq of torrentfile objects.
    """
    return [TorrentFile, TorrentFileV2, TorrentFileHybrid, TorrentAssembler]


@pytest.fixture(scope="package", params=[2**i for i in range(15, 20)])
def sizes(request):
    """
    Generate powers of 2 for file creation package scope.
    """
    size = request.param
    yield size


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


@pytest.fixture()
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


@pytest.fixture(scope="package", params=torrents())
def metafile1(dir1, request):
    """
    Create a standard metafile for testing.
    """
    versions = torrents()
    args = {
        "path": dir1,
        "announce": ["url1", "url2", "url4"],
        "url_list": ["url5", "url6", "url7"],
        "httpseeds": ["url5", "url6", "url7"],
        "comment": "this is a comment",
        "source": "SomeSource",
        "private": 1,
    }
    torrent_class = request.param
    outfile = str(dir1) + str(versions.index(torrent_class)) + ".torrent"
    torrent = torrent_class(**args)
    outfile, _ = torrent.write(outfile=outfile)
    yield outfile
    rmpath(outfile)


@pytest.fixture(params=torrents())
def metafile2(dir2, request):
    """
    Create a standard metafile for testing.
    """
    args = {
        "path": dir2,
        "announce": ["url1", "url4"],
        "url_list": ["url6", "url7"],
        "comment": "this is a comment",
        "httpseeds": ["url6", "url7"],
        "source": "SomeSource",
        "private": 1,
    }
    torrent_class = request.param
    outfile = str(dir2) + ".torrent"
    torrent = torrent_class(**args)
    outfile, _ = torrent.write(outfile=outfile)
    yield outfile


@pytest.fixture(scope="package")
def file1():
    """
    Return the path to a temporary file package scope.
    """
    path = tempfile()
    yield path


@pytest.fixture(scope="package", params=torrents())
def filemeta1(file1, request):
    """
    Test fixture for generating metafile for all versions of torrents.
    """
    args = {
        "path": file1,
        "announce": ["url1", "url4"],
        "url_list": ["url6", "url7"],
        "httpseeds": ["url6", "url7"],
        "comment": "this is a comment",
        "source": "SomeSource",
        "private": 1,
    }
    versions = torrents()
    version = versions.index(request.param)
    name = str(file1) + "file" + str(version) + ".torrent"
    torrent = request.param(**args)
    outfile, _ = torrent.write(outfile=name)
    yield outfile
    rmpath(outfile)


@pytest.fixture(params=torrents())
def filemeta2(file2, request):
    """
    Test fixture for generating a meta file no scope.
    """
    args = {
        "path": file2,
        "announce": ["url1", "url4"],
        "url_list": ["url6", "url7"],
        "httpseeds": ["url7", "url8"],
        "comment": "this is a comment",
        "source": "SomeSource",
        "private": 1,
    }
    versions = torrents()
    version = versions.index(request.param)
    name = str(file2) + "file" + str(version) + ".torrent"
    torrent = request.param(**args)
    outfile, _ = torrent.write(outfile=name)
    yield outfile
    rmpath(outfile)


@pytest.fixture()
def file2():
    """
    Return the path to a temporary file no scope.
    """
    path = tempfile()
    yield path
    rmpath(path)


@pytest.fixture(params=torrents())
def sizedfiles(dir2, sizes, request):
    """
    Generate variable sized meta files for testing, no scope.
    """
    versions = torrents()
    args = {
        "content": dir2,
        "announce": ["url1", "url2", "url4"],
        "url_list": ["url5", "url6", "url7"],
        "comment": "this is a comment",
        "source": "SomeSource",
        "private": 1,
        "piece_length": sizes,
    }
    torrent_class = request.param
    version = str(versions.index(torrent_class))
    outfile = str(dir2) + version + str(sizes) + ".torrent"
    torrent = torrent_class(**args)
    outfile, _ = torrent.write(outfile=outfile)
    yield outfile
    rmpath(outfile)
