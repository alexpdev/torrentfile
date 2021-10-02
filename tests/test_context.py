#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""Testing operation and coverage for context module in tests directory."""

import os
import string
import pytest
from tests.context import (seq, rmpath, rmpaths, tempfile, TD,
                           tempdir, sizedfile, fill_file, fill_folder)


def test_seq():
    """Test seq function for random string output."""
    output = seq()
    assert len([i for i in output if i in string.printable]) > 1


def test_fill_file():
    """Test fill_file function."""
    path = os.path.join(TD, "filledfile.bin")
    fill_file(path, 16)
    assert os.path.exists(path)
    assert os.path.getsize(path) >= 2**16


def test_fill_folder():
    """Test fill_folder function."""
    folder = os.path.join(TD, "filledfolder")
    fill_folder(folder)
    assert os.path.exists(folder)


def test_tempfile():
    """Test tempfile function."""
    filepath = tempfile()
    assert os.path.exists(filepath)


def test_tempdir():
    """Test tempdir function."""
    dirpath = tempdir()
    assert os.path.exists(dirpath)


def test_sizedfile():
    """Test tempdir function."""
    path = sizedfile(16)
    assert os.path.exists(path)
    assert os.path.getsize(path) > 2 ** 16


@pytest.mark.last
def test_rmpath_rmpaths():
    """Test rmpath function and rmpaths function."""
    fillfile = os.path.join(TD, "filledfile.bin")
    fill_file(fillfile, 16)
    sizedpath = sizedfile(16)
    dirpath = tempdir()
    filepath = tempfile()
    fillfolder = os.path.join(TD, "filledfolder")
    fill_folder(fillfolder)
    rmpath(fillfile)
    assert not os.path.exists(fillfile)
    pathlist = [sizedpath, dirpath, filepath, fillfolder]
    rmpaths(pathlist)
    for path in pathlist:
        assert not os.path.exists(path)
