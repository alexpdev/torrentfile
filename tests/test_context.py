#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""Testing operation and coverage for context module in tests directory."""

import os
import string

from tests import context


def test_seq():
    """Test seq function for random string output."""
    output = context.seq()
    assert len([i for i in output if i in string.printable]) > 1  # nosec


def test_fill_file():
    """Test fill_file function."""
    path = os.path.join(context.TESTDIR, "filledfile.bin")
    context.fill_file(path, 16)
    assert os.path.exists(path)  # nosec
    assert os.path.getsize(path) >= 2 ** 16  # nosec
    context.rmpath(path)


def test_contextfill_folder():
    """Test context.fill_folder function."""
    folder = os.path.join(context.TESTDIR, "filledfolder")
    context.fill_folder(folder)
    assert os.path.exists(folder)  # nosec
    context.rmpath(folder)


def test_contexttempfile():
    """Test context.tempfile function."""
    filepath = context.tempfile()
    assert os.path.exists(filepath)  # nosec
    context.rmpath(filepath)


def test_contexttempdir():
    """Test context.tempdir function."""
    dirpath = context.tempdir()
    assert os.path.exists(dirpath)  # nosec
    context.rmpath(dirpath)


def test_contextsizedfile():
    """Test context.tempdir function."""
    path = context.sizedfile(16)
    assert os.path.exists(path)  # nosec
    assert os.path.getsize(path) > 2 ** 16  # nosec
    context.rmpath(path)


def test_rmpath():
    """Test rmpath function."""
    path = context.tempdir()
    assert os.path.exists(path)   # nosec
    context.rmpath(path)
    assert not os.path.exists(path)   # nosec


def test_rmpaths():
    """Test rmpath function."""
    temppaths = [context.sizedfile(20), context.tempfile()]
    assert [os.path.exists(path) for path in temppaths]   # nosec
    context.rmpaths(temppaths)
    assert not any([os.path.exists(path) for path in temppaths])   # nosec
