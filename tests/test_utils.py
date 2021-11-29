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

import math
import os

import pytest

from tests.context import Temp, build, rmpath, testfile
from torrentfile import utils

KIB = 2 ** 10
MIB = KIB ** 2
MIN_BLOCK = 2 ** 14
MAX_BLOCK = MIB * 16


@pytest.fixture(scope="module", params=Temp.structs)
def tdir(request):
    """Return temporary directory."""
    drct = build(request.param)
    yield drct
    rmpath(drct)


@pytest.fixture(scope="module")
def tfile():
    """Return temporary file."""
    tle = testfile()
    yield tle
    rmpath(tle)


def test_get_piece_length_min(tfile):
    """Test get_piece_length function does not fall under minimum."""
    size = os.path.getsize(tfile)
    result = utils.get_piece_length(size)
    assert result >= MIN_BLOCK  # nosec


def test_get_piece_len(tfile):
    """Test get_piece_length function does not exceed max."""
    size = os.path.getsize(tfile)
    result = utils.get_piece_length(size)
    assert result <= MAX_BLOCK  # nosec


def test_get_piece_len_power_2(tfile):
    """Test get_piece_length function is a power of 2."""
    size = os.path.getsize(tfile)
    result = utils.get_piece_length(size)
    assert result % MIN_BLOCK == 0  # nosec


def test_get_piece_len_large():
    """Test get_piece_length function does not exceed maximum."""
    size = 2 ** 31
    result = utils.get_piece_length(size)
    assert result <= MAX_BLOCK  # nosec


def test_path_size_file(tfile):
    """Test path_size function for tempfile."""
    size = os.path.getsize(tfile)
    val = utils.path_size(tfile)
    assert size == val  # nosec


def test_path_size_file_gt0(tfile):
    """Test path_size function for tempfile is greater than zero."""
    val = utils.path_size(tfile)
    assert val > 0  # nosec


def test_path_stat_gt0_filelist(tdir):
    """Test path_stat function for tempdir1 sorted > 0."""
    filelist, _, _ = utils.path_stat(tdir)
    assert len(filelist) > 0  # nosec


def test_path_stat_eq_filelist(tdir):
    """Test path_stat function return filelist."""
    filelist, _, _ = utils.path_stat(tdir)
    assert len(filelist) >= 1  # nosec


def test_path_stat_gt0_size(tdir):
    """Test path_stat function return size > 0."""
    _, size, _ = utils.path_stat(tdir)
    assert size > 0  # nosec


def test_path_stat_eq_size(tdir):
    """Test path_stat function return identically correct size."""
    filelist, size, _ = utils.path_stat(tdir)
    assert size == sum([os.path.getsize(x) for x in filelist])  # nosec


def test_path_stat_gt0_plen(tdir):
    """Test path_stat function return piece length > 0."""
    _, _, piece_length = utils.path_stat(tdir)
    assert piece_length >= MIN_BLOCK  # nosec


def test_path_stat_base2_plen(tdir):
    """Test path_stat function return piece length is power of 2."""
    _, _, piece_length = utils.path_stat(tdir)
    assert piece_length % MIN_BLOCK == 0  # nosec


def test_path_stat_gtsize_plen(tdir):
    """Test path_stat function return size > piece length."""
    _, size, piece_length = utils.path_stat(tdir)
    assert size > piece_length  # nosec


def test_path_piece_length_pow2(tdir):
    """Test path_piece_length for file return piece_length is power of 2."""
    result = utils.path_piece_length(tdir)
    assert result % MIN_BLOCK == 0  # nosec


def test_path_piece_length_min(tdir):
    """Test path_piece_length for dir return piece_length is power of 2."""
    result = utils.path_piece_length(tdir)
    assert result >= MIN_BLOCK  # nosec


def test_path_piece_length_max(tdir):
    """Test path_piece_length for dir return piece_length < Maximum."""
    result = utils.path_piece_length(tdir)
    assert result <= MAX_BLOCK  # nosec


def test_get_filelist_tdir(tdir):
    """Test get_file_list function."""
    result = utils.get_file_list(tdir)
    assert len(result) >= 1  # nosec


def test_get_filelist_tfile(tfile):
    """Test get_file_list function."""
    result = utils.get_file_list(tfile)
    assert len(result) == 1  # nosec


def test_filelist_total_tdir_sum(tdir):
    """Test Utility function filelist_total sum total all files."""
    size, filelist = utils.filelist_total(tdir)
    assert sum([os.path.getsize(fd) for fd in filelist]) == size  # nosec


def test_filelist_total_dir_files(tdir):
    """Test Utility function filelist_total number of files."""
    _, filelist = utils.filelist_total(tdir)
    assert len(filelist) > 0  # nosec


def test_filelist_total_size_tfile(tfile):
    """Test Utility function filelist_total total bytes."""
    size, _ = utils.filelist_total(tfile)
    assert os.path.getsize(tfile) == size  # nosec


def test_filelist_total_len_tfile(tfile):
    """Test Utility function filelist_total length for single."""
    _, filelist = utils.filelist_total(tfile)
    assert len(filelist) == 1  # nosec


def test_filelist_total_tfile(tfile):
    """Test Utility function filelist_total on single file."""
    _, filelist = utils.filelist_total(tfile)
    assert filelist[0] == tfile  # nosec


@pytest.mark.parametrize("piece_length", [14, 20, 2**15, 2**19, "22", "21"])
def test_normalize_plength_type(piece_length):
    """Test normalize piece length function output type."""
    value = utils.normalize_piece_length(piece_length)
    assert isinstance(value, int)   # nosec


@pytest.mark.parametrize("piece_length", [14, 20, 2**15, 2**19, "22", "21"])
def test_normalize_plength_value(piece_length):
    """Test normalize piece length output perfect power of 2."""
    value = utils.normalize_piece_length(piece_length)
    log = math.log2(value)
    assert int(log) == log    # nosec


@pytest.mark.parametrize("piece_length", [10, 1, 4425631, 35, "1111", "abc"])
def test_normalize_plength_fails(piece_length):
    """Test to ensure incorrect piece length values fail."""
    try:
        utils.normalize_piece_length(piece_length)
    except utils.PieceLengthValueError:
        assert True   # nosec


@pytest.mark.parametrize("size", list(range(9, 40)))
def test_humanize_bytes(size):
    """Test humanize bytes function from the utils module."""
    value = 2 ** size
    if value >= 2**30:
        assert "GiB" in utils.humanize_bytes(value)  # nosec
    elif value >= 2**20:
        assert "MiB" in utils.humanize_bytes(value)  # nosec
    elif value >= 2**10:
        assert "KiB" in utils.humanize_bytes(value)  # nosec
    else:
        assert str(value) == utils.humanize_bytes(value)  # nosec
