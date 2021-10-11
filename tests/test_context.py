#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""Testing operation and coverage for context module in tests directory."""

import os
import string

import pytest

from tests.context import (TD, fill_file, fill_folder, rmpath, rmpaths, seq,
                           sizedfile, tempdir, tempfile)


def test_seq():
    """Test seq function for random string output."""
    output = seq()
    assert len([i for i in output if i in string.printable]) > 1  # nosec


def test_fill_file():
    """Test fill_file function."""
    path = os.path.join(TD, "filledfile.bin")
    fill_file(path, 16)
    assert os.path.exists(path)  # nosec
    assert os.path.getsize(path) >= 2 ** 16  # nosec
    rmpath(path)


def test_fill_folder():
    """Test fill_folder function."""
    folder = os.path.join(TD, "filledfolder")
    fill_folder(folder)
    assert os.path.exists(folder)  # nosec
    rmpath(folder)


def test_tempfile():
    """Test tempfile function."""
    filepath = tempfile()
    assert os.path.exists(filepath)  # nosec
    rmpath(filepath)


def test_tempdir():
    """Test tempdir function."""
    dirpath = tempdir()
    assert os.path.exists(dirpath)  # nosec
    rmpath(dirpath)


def test_sizedfile():
    """Test tempdir function."""
    path = sizedfile(16)
    assert os.path.exists(path)  # nosec
    assert os.path.getsize(path) > 2 ** 16  # nosec
    rmpath(path)


@pytest.mark.last
def test_rmpath_rmpaths():
    """Test rmpath function and rmpaths function."""
    dirpath = tempdir()
    filepath = tempfile()
    sizedpath = sizedfile(16)
    fillfile = os.path.join(TD, "filledfile.bin")
    fillfolder = os.path.join(TD, "filledfolder")
    fill_file(fillfile, 16)
    fill_folder(fillfolder)
    rmpath(fillfile)
    assert not os.path.exists(fillfile)  # nosec
    pathlist = [sizedpath, dirpath, filepath, fillfolder]
    rmpaths(pathlist)
    for path in pathlist:
        assert not os.path.exists(path)  # nosec
