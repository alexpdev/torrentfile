#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""Testing operation and coverage for context module in tests directory."""

import os

import pytest

from tests.context import Temp, build, mkdirs, rmpath, teardown, testfile


def spaths():
    """Return a list of each file in all structs."""
    paths = [j for i in Temp.structs for j in i]
    return paths


def test_seq():
    """Test seq function for random string output."""
    output = Temp.seq
    assert isinstance(output, str)   # nosec


def test_structs():
    """Test temp directory structures."""
    assert len(Temp.structs) == 3   # nosec


@pytest.mark.parametrize("struct", spaths())
def test_mkdirs(struct):
    """Test mkdirs function from context module."""
    fd = mkdirs(struct)
    assert os.path.exists(os.path.dirname(fd))   # nosec
    rmpath(os.path.dirname(fd))


@pytest.mark.parametrize("struct", spaths())
def test_rmpath(struct):
    """Test rmpath function from context module."""
    fd = os.path.dirname(mkdirs(struct))
    rmpath(fd)
    assert not os.path.exists(fd)   # nosec
    rmpath(fd)


def test_xz_teardown():
    """Test teardown function from context module."""
    teardown()
    assert not os.path.exists(Temp.root)   # nosec
    os.mkdir(Temp.root)


@pytest.mark.parametrize("size", list(range(14, 27)))
def test_testfile_func(size):
    """Test testfile function result exists from context module."""
    path = testfile(exp=size)
    assert os.path.exists(path)   # nosec
    rmpath(path)


@pytest.mark.parametrize("size", list(range(14, 27)))
def test_testfile_func1(size):
    """Test testfile function result size from context module."""
    path = testfile(exp=size)
    assert os.path.getsize(path) == 2**size   # nosec
    rmpath(path)


@pytest.mark.parametrize("start", list(range(14, 20)))
@pytest.mark.parametrize("stop", list(range(21, 27)))
@pytest.mark.parametrize("struct", Temp.structs)
def test_build_func(struct, start, stop):
    """Test testfile function result size from context module."""
    root = build(struct, start, stop)
    assert os.path.exists(root)   # nosec
    rmpath(root)
