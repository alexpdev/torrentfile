#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""Testing operation and coverage for context module in tests directory."""

import os

from tests import context


def test_seq():
    """Test seq function for random string output."""
    output = context.seq()
    assert isinstance(output, str)  # nosec


def test_fill_file():
    """Test fill_file function."""
    path = os.path.join(context.TESTDIR, "filledfile.bin")
    context.fill_file(path, 16)
    assert os.path.exists(path)  # nosec
    assert os.path.getsize(path) >= 2 ** 16  # nosec
    context.rmpath(path)


def test_fill_folder():
    """Test context.fill_folder function."""
    folder = os.path.join(context.TESTDIR, "filledfolder")
    context.fill_folder([folder], [])
    assert os.path.exists(folder)  # nosec
    context.rmpath(folder)


def test_fill_folder2():
    """Test context.fill_folder function."""
    folder = os.path.join(context.TESTDIR, "filledfolder")
    os.mkdir(folder)
    file1 = os.path.join(folder, "file1")
    with open(file1, "wb") as fd:
        fd.write(b"afdsfdsa")
    context.fill_folder([folder], [(file1, 14)])
    assert os.path.exists(folder)  # nosec
    context.rmpath(folder)


def test_teardown():
    """Test teardown function."""
    context.teardown()
    assert not os.path.exists(context.TESTDIR)   # nosec
    context.datadir(lambda x: 10)


def test_tempdir1():
    """Test context.tempdir function."""
    dirpath = context.tempdir1()
    assert os.path.exists(dirpath)  # nosec
    context.rmpath(dirpath)


def test_tempdir2():
    """Test context.tempdir function."""
    dirpath = context.tempdir2()
    assert os.path.exists(dirpath)  # nosec
    context.rmpath(dirpath)


def test_tempdir3():
    """Test context.tempdir function."""
    dirpath = context.tempdir3()
    assert os.path.exists(dirpath)  # nosec
    context.rmpath(dirpath)


def test_sizedfile():
    """Test context.tempdir function."""
    path = context.sizedfile(16)
    assert os.path.exists(path)  # nosec
    assert os.path.getsize(path) >= 2 ** 16  # nosec
    context.rmpath(path)


def test_rmpath():
    """Test rmpath function."""
    path = context.tempdir1()
    assert os.path.exists(path)   # nosec
    context.rmpath(path)
    assert not os.path.exists(path)   # nosec


def test_rmpaths():
    """Test rmpath function."""
    temppaths = [context.sizedfile(20), context.tempfile()]
    assert [os.path.exists(path) for path in temppaths]   # nosec
    context.rmpaths(temppaths)
    assert [os.path.exists(i) for i in temppaths] == [False, False]   # nosec
