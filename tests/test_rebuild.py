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
Testing functions for the rebuild sub-action commands from command line args.
"""
import os

import pyben
import pytest

from tests import dir1, file1, file2, filemeta1, filemeta2, rmpath
from torrentfile.commands import rebuild
from torrentfile.hasher import FileHasher, HasherHybrid, HasherV2
from torrentfile.rebuild import Assembler
from torrentfile.torrent import TorrentAssembler, TorrentFile


def test_fix():
    """Test that the fixtures import properly."""
    assert filemeta2 and dir1 and file1 and filemeta1 and file2


def create_torrentfile(path, creator, dest, piece_length):
    """
    Create a new torrent metafile based on the provided parameters.
    """
    torrent = creator(path=path, outfile=dest, piece_length=piece_length)
    data = torrent.write()
    return data


def create_dest():
    """
    Create the destination directory for testing the rebuild function.
    """
    parent = os.path.dirname(__file__)
    dest = os.path.join(parent, "dest2")
    if os.path.exists(dest):
        rmpath(dest)
        os.mkdir(dest)
    return dest


@pytest.mark.parametrize("creator", [TorrentFile, TorrentAssembler])
@pytest.mark.parametrize("size", list(range(15, 19)))
def test_rebuilder_with_dir(dir1, creator, size):
    """
    Test that the rebuilder works with full directories.
    """
    dest = create_dest()
    contents = [os.path.dirname(dir1)]
    outfile = dir1 + ".torrent"
    create_torrentfile(dir1, creator, outfile, size)
    assembler = Assembler(contents, contents, dest)
    counter = assembler.assemble_torrents()
    assert counter > 0


def get_params(path):
    """
    Shortcut method for building the parameters provided by fixtures.
    """
    base = os.path.dirname(path)
    out = os.path.join(os.path.dirname(base), "dest")
    if os.path.exists(out):
        rmpath(out)  # pragma: nocover
    os.mkdir(out)
    return ([path], [base], out)


@pytest.fixture()
def single1(filemeta1):
    """Test fixture for testing the build subcommand."""
    params = get_params(filemeta1)
    return params


@pytest.fixture()
def single2(filemeta2):
    """Test fixture testing build with mismatched file size."""
    params = get_params(filemeta2)
    return params


def test_single_file(single1):
    """
    Test functionality of single file torrent and single torrent.
    """
    assembler = Assembler(*single1)
    counter = assembler.assemble_torrents()
    assert counter > 0


def test_single_file_smaller(single2):
    """
    Test functionality of single file torrent and single torrent.
    """
    name = pyben.load(single2[0][0])["info"]["name"]
    contents = os.path.join(single2[1][0], name)
    with open(contents, "rb") as content:
        data = content.read()
    with open(contents, "wb") as content:
        content.write(data[: len(data) // 2])
    assembler = Assembler(*single2)
    counter = assembler.assemble_torrents()
    assert counter == 0


def test_wrong_path():
    """Test rebuild command with incorrect paths."""

    class Namespace:
        """
        Emulates the behaviour of argparse.Namespace.
        """

        metafiles = "/non/existent/path"
        destination = "/non/existing/path"
        contents = "/non/existing/path"

    try:
        rebuild(Namespace)
    except FileNotFoundError:
        assert True


@pytest.mark.parametrize("size", [2**i for i in range(14, 21)])
def test_file1_hashers(file2, size):
    """Test that all three of the version2 hashers produce the same result."""
    hasher1 = HasherHybrid(file2, size, progress=False)
    hasher2 = HasherV2(file2, size, progress=False)
    hasher3 = FileHasher(file2, size, progress=False)
    _ = list(hasher3)
    lst = [hasher1.root, hasher2.root, hasher3.root]
    print(lst)
    assert len(set(lst)) == 1
