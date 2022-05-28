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
from torrentfile.rebuild import Assembler


def test_fix():
    """Test that the fixtures import properly."""
    assert filemeta2 and dir1 and file1 and filemeta1 and file2


def get_params(path):
    """
    Shortcut method for building the parameters provided by fixtures.
    """
    base = os.path.dirname(path)
    out = os.path.join(os.path.dirname(base), "dest")
    if os.path.exists(out):
        rmpath(out)  # pragma: nocover
    os.mkdir(out)
    return (path, base, out)


@pytest.fixture()
def single1(filemeta1):
    """Test fixture for testing the build subcommand."""
    params = get_params(filemeta1)
    yield params
    rmpath(params[-1])


@pytest.fixture()
def single2(filemeta2):
    """Test fixture testing build with mismatched file size."""
    params = get_params(filemeta2)
    yield params
    rmpath(params[-1])


def test_single_file(single1):
    """
    Test functionality of single file torrent and single torrent.
    """
    assembler = Assembler(*single1)
    counter = assembler.rebuild()
    assert counter > 0


def test_single_file_smaller(single2):
    """
    Test functionality of single file torrent and single torrent.
    """
    name = pyben.load(single2[0])["info"]["name"]
    contents = os.path.join(single2[1], name)
    with open(contents, "rb") as content:
        data = content.read()
    with open(contents, "wb") as content:
        content.write(data[: len(data) // 2])
    assembler = Assembler(*single2)
    counter = assembler.rebuild()
    assert counter == 0
