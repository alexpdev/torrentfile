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
Testing functions for the torrent module.
"""
import os

import pytest

from tests import dir1, dir2, rmpath, tempfile, torrents
from torrentfile.mixins import ProgMixin, waiting
from torrentfile.torrent import MetaFile
from torrentfile.utils import MissingPathError


def test_fixtures():
    """
    Test pytest fixtures.
    """
    assert dir1 and dir2


@pytest.mark.parametrize("version", torrents())
def test_torrentfile_missing_path(version):
    """
    Test missing path error exception.
    """
    try:
        version()
    except MissingPathError:
        assert True


def test_metafile_assemble(dir1):
    """
    Test assembling base metafile exception.
    """
    metafile = MetaFile(path=dir1)
    try:
        metafile.assemble()
    except NotImplementedError:
        assert True


@pytest.mark.parametrize("version", torrents())
def test_torrentfile_one_empty(dir2, version):
    """
    Test creating a torrent meta file with given directory plus extra.
    """
    a = next(os.walk(dir2))
    if len(a[-1]) > 0:
        with open(os.path.join(a[0], a[-1][0]), "w", encoding="utf-8") as _:
            pass
    args = {
        "path": dir2,
        "comment": "somecomment",
        "announce": "announce",
    }
    torrent = version(**args)
    assert torrent.meta["announce"] == "announce"


@pytest.mark.parametrize("version", torrents())
def test_torrentfile_extra(dir2, version):
    """
    Test creating a torrent meta file with given directory plus extra.
    """

    def walk(item):
        """
        Edit files in directory structure.
        """
        if item.is_file():
            with open(item, "ab") as binfile:
                binfile.write(bytes(1000))
        elif item.is_dir():
            for sub in item.iterdir():
                walk(sub)

    walk(dir2)
    args = {
        "path": dir2,
        "comment": "somecomment",
        "announce": "announce",
    }
    torrent = version(**args)
    assert torrent.meta["announce"] == "announce"


@pytest.mark.parametrize("num", list(range(17, 25)))
@pytest.mark.parametrize("piece_length", [2**i for i in range(14, 18)])
@pytest.mark.parametrize("version", torrents())
def test_torrentfile_single(version, num, piece_length, capsys):
    """
    Test creating a torrent file from a single file contents.
    """
    tfile = tempfile(exp=num)
    with capsys.disabled():
        version.set_callback(print)
    outfile = str(tfile) + ".torrent"
    args = {
        "path": tfile,
        "comment": "somecomment",
        "announce": "announce",
        "piece_length": piece_length,
        "outfile": outfile,
    }
    trent = version(**args)
    trent.write()
    assert os.path.exists(outfile)
    rmpath(tfile, str(tfile) + ".torrent")


@pytest.mark.parametrize("size", list(range(17, 25)))
@pytest.mark.parametrize("piece_length", [2**i for i in range(14, 18)])
@pytest.mark.parametrize("version", torrents())
def test_torrentfile_single_extra(version, size, piece_length):
    """
    Test creating a torrent file from a single file contents plus extra.
    """
    tfile = tempfile(exp=size)
    with open(tfile, "ab") as binfile:
        binfile.write(bytes(str(tfile).encode("utf-8")))
    outfile = str(tfile) + ".torrent"
    args = {
        "path": tfile,
        "comment": "somecomment",
        "announce": "announce",
        "piece_length": piece_length,
        "outfile": outfile,
    }
    torrent = version(**args)
    torrent.write()
    assert os.path.exists(outfile)
    rmpath(tfile, outfile)


@pytest.mark.parametrize("sze", list(range(17, 25)))
@pytest.mark.parametrize("piecelength", [2**i for i in range(14, 18)])
@pytest.mark.parametrize("ver", torrents())
def test_torrentfile_single_under(ver, sze, piecelength):
    """
    Test creating a torrent file from less than a single file contents.
    """
    tfile = tempfile(exp=sze)
    with open(tfile, "rb") as binfile:
        data = binfile.read()
    with open(tfile, "wb") as binfile:
        binfile.write(data[:-(2**9)])
    outfile = str(tfile) + ".torrent"
    kwargs = {
        "path": tfile,
        "comment": "somecomment",
        "announce": "announce",
        "piece_length": piecelength,
        "outfile": outfile,
    }
    torrent = ver(**kwargs)
    outfile, _ = torrent.write()
    assert os.path.exists(outfile)
    rmpath(tfile, outfile)


def test_create_cwd_fail():
    """Test cwd argument with create command failure."""

    class SuFile:
        """A mock admin file."""

        @staticmethod
        def __fspath__():
            raise PermissionError

        def __str__(self):
            return "SuFile"

    tfile = tempfile()
    torrent = MetaFile(path=tfile)
    sufile = SuFile()
    try:
        assert torrent.write(outfile=sufile)
    except PermissionError:
        assert True
    rmpath(tfile)


def test_waiting_mixin():
    """
    Test waiting function.
    """
    msg = "Testing message"
    lst = []
    timeout = 3
    waiting(msg, lst, timeout=timeout)
    assert len(lst) == 0


@pytest.mark.parametrize("version", torrents())
@pytest.mark.parametrize("progress", [0, 1, 2])
def test_mbtorrent(version, progress):
    """
    Test torrent creation for file size larger than 10MB.
    """
    tfile = tempfile(exp=26)
    outfile = str(tfile) + ".torrent"
    args = {
        "path": tfile,
        "progress": progress,
        "piece_length": "14",
        "outfile": outfile,
        "align": True,
    }
    torrent = version(**args)
    outfile, _ = torrent.write()
    assert os.path.exists(outfile)
    rmpath(tfile, outfile)


@pytest.mark.parametrize("params", [(10, 12), (10, 15), (20, 25), (28, 32)])
def test_progress_bar(params):
    """Testing the prog mixin with various sizes."""
    increment, total = params
    progbar = ProgMixin()
    progbar.prog_start(1 << total, "some/fake/path")
    while progbar.prog.state < total:
        progbar.prog_update(1 << increment)
    assert progbar.prog.state >= total
