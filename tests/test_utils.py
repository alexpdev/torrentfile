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
from torrentfile.utils import (get_file_list, get_piece_length,
                               path_size, path_stat,
                               path_piece_length, Bendecoder,
                               Benencoder)
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

@pytest.fixture
def metadata():
    meta = {"announce": "https://tracker.com:2017/announce",
            "created by": "torrentfile",
            "piece length": MAX_BLOCK,
            "info": {"name": "torrentname.bin",
            "files": [{"length": 2**28, "path": ["path", "to", "content"]},
                    {"length": 2**28, "path": ["path", "more","content"]}],
            "pieces": b'some bytes of data',
            "source": "tracker", "private": 1}}
    return meta

@pytest.fixture
def bencode(metadata):
    encoder = Benencoder(metadata)
    data = encoder.encode()
    return data

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

def test_get_piece_len_large():
    s = 2**31
    result = get_piece_length(s)
    assert result <= MAX_BLOCK

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

def test_get_file_list_dir_sort(tdir):
    results = get_file_list(tdir, sort=True)
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

def test_path_piece_length_pow2(tdir):
    result = path_piece_length(tdir)
    assert result % MIN_BLOCK == 0

def test_path_piece_length_min(tdir):
    result = path_piece_length(tdir)
    assert result >= MIN_BLOCK

def test_path_piece_length_max(tdir):
    result = path_piece_length(tdir)
    assert result <= MAX_BLOCK

def test_encode(metadata):
    encoder = Benencoder(metadata)
    data = encoder.encode()
    assert data is not None

def test_encode_type(metadata):
    encoder = Benencoder(metadata)
    data = encoder.encode()
    assert isinstance(data, bytes)

def test_decode(bencode):
    decoder = Bendecoder(bencode)
    data = decoder.decode()
    assert data is not None

def test_decode_type(bencode):
    decoder = Bendecoder(bencode)
    data = decoder.decode()
    assert isinstance(data, dict)

def test_decode_type_info(bencode):
    decoder = Bendecoder(bencode)
    data = decoder.decode()
    assert "info" in data

def test_decode_type_announce(bencode):
    decoder = Bendecoder(bencode)
    data = decoder.decode()
    assert "announce" in data

def test_decode_type_piecelength(bencode):
    decoder = Bendecoder(bencode)
    data = decoder.decode()
    assert "piece length" in data

def test_decode_type_created_by(bencode):
    decoder = Bendecoder(bencode)
    data = decoder.decode()
    assert "created by" in data
