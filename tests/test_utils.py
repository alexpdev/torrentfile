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
import random

from tests.context import testdir, testfile
from torrentfile.utils import ( get_file_list,
                                get_piece_length,
                                path_size,
                                path_stat)

KIB = 2 ** 10
MIB = KIB ** 2
GIB = KIB ** 3
MIN_BLOCK = 2 ** 14
MAX_BLOCK = MIB * 16


def test_get_piece_len(testfile):
    s = os.path.getsize(testfile)
    result = get_piece_length(s)
    assert result > 0

def test_get_piece_length_min(testfile):
    s = os.path.getsize(testfile)
    result = get_piece_length(s)
    assert result >= MIN_BLOCK

def test_get_piece_len(testfile):
    s = os.path.getsize(testfile)
    result = get_piece_length(s)
    assert result <= MAX_BLOCK

def test_get_piece_len_power_2(testfile):
    s = os.path.getsize(testfile)
    result = get_piece_length(s)
    assert result % MIN_BLOCK == 0

def test_path_size_file(testfile):
    s = os.path.getsize(testfile)
    val = path_size(testfile)
    assert s == val

def test_path_size_file_gt0(testfile):
    val = path_size(testfile)
    assert val > 0

def test_path_size_dir_gt0(testdir):
    val = path_size(testdir)
    current = os.path.join(os.path.dirname(os.path.abspath(__file__)),"testdir")
    temp1 = os.path.join(current,"testing\\temp_data.dat")
    temp2 = os.path.join(current,"testing\\temp_text.txt")
    temp3 = os.path.join(current,"temp_dir\\temp_data.dat")
    temp4 = os.path.join(current,"temp_dir\\temp_text.txt")
    size = sum([os.path.getsize(x) for x in [temp1,temp2,temp3,temp4]])
    assert size == val

def test_get_file_list_file(testfile):
    results = get_file_list(testfile)
    assert len(results) == 1

def test_get_file_list_dir(testdir):
    results = get_file_list(testdir)
    assert len(results) == 4

def test_path_stat_gt0_filelist(testdir):
    filelist, _, _ = path_stat(testdir)
    assert len(filelist) > 0

def test_path_stat_eq_filelist(testdir):
    filelist, _, _ = path_stat(testdir)
    assert len(filelist) == 4

def test_path_stat_gt0_size(testdir):
    _, size, _ = path_stat(testdir)
    assert size > 0

def test_path_stat_eq_size(testdir):
    filelist, size, _ = path_stat(testdir)
    assert size == sum([os.path.getsize(x) for x in filelist])

def test_path_stat_gt0_plen(testdir):
    _, _, piece_length = path_stat(testdir)
    assert piece_length >= MIN_BLOCK

def test_path_stat_base2_plen(testdir):
    _, _, piece_length = path_stat(testdir)
    assert piece_length % MIN_BLOCK == 0

def test_path_stat_gtsize_plen(testdir):
    _, size, piece_length = path_stat(testdir)
    assert size > piece_length
