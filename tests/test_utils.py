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
"""Test functions for utils module."""

import os

import pytest

from tests.context import rmpath, tempdir, tempfile
from torrentfile.utils import (get_piece_length, path_piece_length, path_size,
                               path_stat)

KIB = 2 ** 10
MIB = KIB ** 2
MIN_BLOCK = 2 ** 14
MAX_BLOCK = MIB * 16


@pytest.fixture(scope="module")
def tdir():
    """Return temporary directory."""
    drct = tempdir()
    yield drct
    rmpath(drct)


@pytest.fixture(scope="module")
def tfile():
    """Return temporary file."""
    testfile = tempfile()
    yield testfile
    rmpath(testfile)


@pytest.fixture
def metadata():
    """Return preconfigured metadata."""
    meta = {
        "announce": "https://tracker.com:2017/announce",
        "created by": "torrentfile",
        "piece length": MAX_BLOCK,
        "info": {
            "name": "torrentname.bin",
            "files": [
                {"length": 2 ** 28, "path": ["path", "to", "content"]},
                {"length": 2 ** 28, "path": ["path", "more", "content"]},
            ],
            "pieces": b"some bytes of data",
            "source": "tracker",
            "private": 1,
        },
    }
    return meta


def test_get_piece_length_min(tfile):
    """Test get_piece_length function does not fall under minimum."""
    size = os.path.getsize(tfile)
    result = get_piece_length(size)
    assert result >= MIN_BLOCK  # nosec


def test_get_piece_len(tfile):
    """Test get_piece_length function does not exceed max."""
    size = os.path.getsize(tfile)
    result = get_piece_length(size)
    assert result <= MAX_BLOCK  # nosec


def test_get_piece_len_power_2(tfile):
    """Test get_piece_length function is a power of 2."""
    size = os.path.getsize(tfile)
    result = get_piece_length(size)
    assert result % MIN_BLOCK == 0  # nosec


def test_get_piece_len_large():
    """Test get_piece_length function does not exceed maximum."""
    size = 2 ** 31
    result = get_piece_length(size)
    assert result <= MAX_BLOCK  # nosec


def test_path_size_file(tfile):
    """Test path_size function for tempfile."""
    size = os.path.getsize(tfile)
    val = path_size(tfile)
    assert size == val  # nosec


def test_path_size_file_gt0(tfile):
    """Test path_size function for tempfile is greater than zero."""
    val = path_size(tfile)
    assert val > 0  # nosec


def test_path_stat_gt0_filelist(tdir):
    """Test path_stat function for tempdir sorted > 0."""
    filelist, _, _ = path_stat(tdir)
    assert len(filelist) > 0  # nosec


def test_path_stat_eq_filelist(tdir):
    """Test path_stat function return filelist."""
    filelist, _, _ = path_stat(tdir)
    assert len(filelist) > 1  # nosec


def test_path_stat_gt0_size(tdir):
    """Test path_stat function return size > 0."""
    _, size, _ = path_stat(tdir)
    assert size > 0  # nosec


def test_path_stat_eq_size(tdir):
    """Test path_stat function return identically correct size."""
    filelist, size, _ = path_stat(tdir)
    assert size == sum([os.path.getsize(x) for x in filelist])  # nosec


def test_path_stat_gt0_plen(tdir):
    """Test path_stat function return piece length > 0."""
    _, _, piece_length = path_stat(tdir)
    assert piece_length >= MIN_BLOCK  # nosec


def test_path_stat_base2_plen(tdir):
    """Test path_stat function return piece length is power of 2."""
    _, _, piece_length = path_stat(tdir)
    assert piece_length % MIN_BLOCK == 0  # nosec


def test_path_stat_gtsize_plen(tdir):
    """Test path_stat function return size > piece length."""
    _, size, piece_length = path_stat(tdir)
    assert size > piece_length  # nosec


def test_path_piece_length_pow2(tdir):
    """Test path_piece_length for file return piece_length is power of 2."""
    result = path_piece_length(tdir)
    assert result % MIN_BLOCK == 0  # nosec


def test_path_piece_length_min(tdir):
    """Test path_piece_length for dir return piece_length is power of 2."""
    result = path_piece_length(tdir)
    assert result >= MIN_BLOCK  # nosec


def test_path_piece_length_max(tdir):
    """Test path_piece_length for dir return piece_length < Maximum."""
    result = path_piece_length(tdir)
    assert result <= MAX_BLOCK  # nosec
