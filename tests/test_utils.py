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

import os
import pytest
from torrentfile.utils import (get_file_list, get_piece_length, path_size,
                               path_stat)
from tests.context import tempfile, tempdir, rmpath

KIB = 2 ** 10
MIB = KIB ** 2
GIB = KIB ** 3
MIN_BLOCK = 2 ** 14
MAX_BLOCK = MIB * 16

@pytest.fixture(scope="module")
def tdir():
    folder = tempdir()
    yield folder
    rmpath(folder)

@pytest.fixture(scope="module")
def tfile():
    fd = tempfile()
    yield fd
    rmpath(fd)



def test_get_piece_len(tfile):
    s = os.path.getsize(tfile)
    result = get_piece_length(s)
    assert result > 0


def test_get_piece_length_min(tfile):
    s = os.path.getsize(tfile)
    result = get_piece_length(s)
    assert result >= MIN_BLOCK


def test_get_piece_len(tfile):
    s = os.path.getsize(tfile)
    result = get_piece_length(s)
    assert result <= MAX_BLOCK


def test_get_piece_len_power_2(tfile):
    s = os.path.getsize(tfile)
    result = get_piece_length(s)
    assert result % MIN_BLOCK == 0


def test_path_size_file(tfile):
    s = os.path.getsize(tfile)
    val = path_size(tfile)
    assert s == val


def test_path_size_file_gt0(tfile):
    val = path_size(tfile)
    assert val > 0

def test_get_file_list_file(tfile):
    results = get_file_list(tfile)
    assert len(results) == 1


def test_get_file_list_dir(tdir):
    results = get_file_list(tdir)
    assert len(results) > 1


def test_path_stat_gt0_filelist(tdir):
    filelist, _, _ = path_stat(tdir)
    assert len(filelist) > 0


def test_path_stat_eq_filelist(tdir):
    filelist, _, _ = path_stat(tdir)
    assert len(filelist) > 1


def test_path_stat_gt0_size(tdir):
    _, size, _ = path_stat(tdir)
    assert size > 0


def test_path_stat_eq_size(tdir):
    filelist, size, _ = path_stat(tdir)
    assert size == sum([os.path.getsize(x) for x in filelist])


def test_path_stat_gt0_plen(tdir):
    _, _, piece_length = path_stat(tdir)
    assert piece_length >= MIN_BLOCK


def test_path_stat_base2_plen(tdir):
    _, _, piece_length = path_stat(tdir)
    assert piece_length % MIN_BLOCK == 0


def test_path_stat_gtsize_plen(tdir):
    _, size, piece_length = path_stat(tdir)
    assert size > piece_length
