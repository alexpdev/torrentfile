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
"""Unittest functions for testing torrentfile utils module."""
import math

import pytest

from tests import dir1, dir2, rmpath
from torrentfile import utils


@pytest.mark.parametrize("size", [156634528, 2 ** 30, 67987, 16384, 8563945])
def test_get_piece_length(size):
    """Test function for best piece length for given size."""
    value = utils.get_piece_length(size)
    assert value % 1024 == 0


@pytest.mark.parametrize("size", [156634528, 2 ** 30, 67987, 16384, 8563945])
def test_get_piece_length_max(size):
    """Test function for best piece length for given size maximum."""
    value = utils.get_piece_length(size)
    assert value < 2 ** 27


@pytest.mark.parametrize("size", [156634528, 2 ** 30, 67987, 16384, 8563945])
def test_get_piece_length_min(size):
    """Test function for best piece length for given size minimum."""
    value = utils.get_piece_length(size)
    assert value >= 2 ** 14


def test_get_path_length_mod(dir1):
    """Test function for the best piece length for provided path."""
    assert utils.path_piece_length(dir1) % (2 ** 14) == 0


def test_get_path_length_min(dir1):
    """Test function for getting piece length for folders min."""
    assert utils.path_piece_length(dir1) >= (2 ** 14)


def test_get_path_length_max(dir1):
    """Test function for getting piece length for folders max."""
    assert utils.path_piece_length(dir1) <= (2 ** 27)


def test_path_stat(dir1):
    """Test function for acquiring piece length information on folder."""
    _, _, piece_length = utils.path_stat(dir1)
    assert piece_length % (2 ** 14) == 0


def test_path_stat_size(dir1):
    """Test function for acquiring total size information on folder."""
    _, totalsize, _ = utils.path_stat(dir1)
    assert totalsize == (2 ** 18) * 4


def test_path_stat_filelist_size(dir1):
    """Test function for acquiring file list information on folder."""
    filelist, _, _ = utils.path_stat(dir1)
    assert len(filelist) == 4


def test_get_filelist(dir1):
    """Test function for get a list of files in a directory."""
    filelist = utils.get_file_list(dir1)
    assert len(filelist) == 4


def test_get_path_size(dir1):
    """Test function for getting total size of directory."""
    pathsize = utils.path_size(dir1)
    assert pathsize == (2 ** 18) * 4


def test_filelist_total(dir1):
    """Test function for acquiring a filelist for directory."""
    total, _ = utils.filelist_total(dir1)
    assert total == (2 ** 18) * 4


def test_piecelength_error_fixtures():
    """Test exception for uninterpretable piece length value."""
    try:
        raise utils.PieceLengthValueError("message")
    except utils.PieceLengthValueError:
        assert True
        assert dir1


def test_missing_path_error():
    """Test exception for missing path parameter."""
    try:
        raise utils.MissingPathError("message")
    except utils.MissingPathError:
        assert True
        assert dir2


@pytest.mark.parametrize("value", [5, 32, 18, 225, 16384, 256000])
def test_next_power_2(value):
    """Test next power of 2 function in utils module."""
    result = utils.next_power_2(value)
    log = math.log2(result)
    assert log == int(log)
    assert result % 2 == 0
    assert result >= value


@pytest.mark.parametrize(
    "amount, result",
    [
        (100, "100"),
        (1100, "1 KiB"),
        (1_100_000, "1 MiB"),
        (1_100_000_000, "1 GiB"),
    ],
)
def test_humanize_bytes(amount, result):
    """Test humanize bytes function."""
    assert utils.humanize_bytes(amount) == result


@pytest.mark.parametrize("amount, result", [(i, 2 ** i) for i in range(14, 21)])
def test_normalize_piece_length_int(amount, result):
    """Test normalize piece length function.

    Parameters
    ----------
    amount : `str` or `int`
        piece length or representation
    result : int
        expected output.
    """
    assert utils.normalize_piece_length(amount) == result


@pytest.mark.parametrize(
    "amount, result", [(str(i), 2 ** i) for i in range(14, 21)]
)
def test_normalize_piece_length_str(amount, result):
    """Test normalize piece length function.

    Parameters
    ----------
    amount : `str` or `int`
        piece length or representation
    result : int
        expected output.
    """
    assert utils.normalize_piece_length(amount) == result


@pytest.mark.parametrize(
    "amount", ["hello", 11, 0, 100000, 28, "zero", "fifteen"]
)
def test_norm_plength_errors(amount):
    """Test function to normalize piece length errors.

    Parameters
    ----------
    amount : any
        arguments intended to raise an exception.
    """
    try:
        assert utils.normalize_piece_length(amount)
    except utils.PieceLengthValueError:
        assert True


def test_filelisttotal_missing(dir2):
    """Test function filelist total with missing path.

    Parameters
    ----------
    dir2 : pytest.fixture
        fixture containing a temporary directory
    """
    rmpath(dir2)
    try:
        utils.filelist_total(dir2)
    except utils.MissingPathError:
        assert True
