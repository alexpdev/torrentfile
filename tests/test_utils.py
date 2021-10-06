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
from torrentfile.utils import (get_file_list, get_piece_length,
                               path_size, path_stat,
                               path_piece_length, Bendecoder,
                               Benencoder)
from tests.context import tempfile, tempdir, rmpath

KIB = 2 ** 10
MIB = KIB ** 2
MIN_BLOCK = 2 ** 14
MAX_BLOCK = MIB * 16


@pytest.fixture(scope="module")
def tdir():
    """Return temporary directory."""
    folder = tempdir()
    yield folder
    rmpath(folder)


@pytest.fixture(scope="module")
def tfile():
    """Return temporary file."""
    fd = tempfile()
    yield fd
    rmpath(fd)


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
                {
                    "length": 2**28,
                    "path": ["path", "to", "content"]
                },
                {
                    "length": 2**28,
                    "path": ["path", "more", "content"]
                }
            ],
            "pieces": b'some bytes of data',
            "source": "tracker",
            "private": 1
        }
    }
    return meta


@pytest.fixture
def bencode(metadata):
    """Test encoding in bencode format."""
    encoder = Benencoder(metadata)
    data = encoder.encode()
    return data


def test_get_piece_length_min(tfile):
    """Test get_piece_length function does not fall under minimum."""
    s = os.path.getsize(tfile)
    result = get_piece_length(s)
    assert result >= MIN_BLOCK


def test_get_piece_len(tfile):
    """Test get_piece_length function does not exceed max."""
    s = os.path.getsize(tfile)
    result = get_piece_length(s)
    assert result <= MAX_BLOCK


def test_get_piece_len_power_2(tfile):
    """Test get_piece_length function is a power of 2."""
    s = os.path.getsize(tfile)
    result = get_piece_length(s)
    assert result % MIN_BLOCK == 0


def test_get_piece_len_large():
    """Test get_piece_length function does not exceed maximum."""
    s = 2**31
    result = get_piece_length(s)
    assert result <= MAX_BLOCK


def test_path_size_file(tfile):
    """Test path_size function for tempfile."""
    s = os.path.getsize(tfile)
    val = path_size(tfile)
    assert s == val


def test_path_size_file_gt0(tfile):
    """Test path_size function for tempfile is greater than zero."""
    val = path_size(tfile)
    assert val > 0


def test_get_file_list_file(tfile):
    """Test get_file_list function for tempfile."""
    results = get_file_list(tfile)
    assert len(results) == 1


def test_get_file_list_dir(tdir):
    """Test get_file_list function for tempdir."""
    results = get_file_list(tdir)
    assert len(results) > 1


def test_get_file_list_dir_sort(tdir):
    """Test get_file_list function for tempdir sorted."""
    results = get_file_list(tdir, sort=True)
    assert len(results) > 1


def test_path_stat_gt0_filelist(tdir):
    """Test path_stat function for tempdir sorted > 0."""
    filelist, _, _ = path_stat(tdir)
    assert len(filelist) > 0


def test_path_stat_eq_filelist(tdir):
    """Test path_stat function return filelist."""
    filelist, _, _ = path_stat(tdir)
    assert len(filelist) > 1


def test_path_stat_gt0_size(tdir):
    """Test path_stat function return size > 0."""
    _, size, _ = path_stat(tdir)
    assert size > 0


def test_path_stat_eq_size(tdir):
    """Test path_stat function return identically correct size."""
    filelist, size, _ = path_stat(tdir)
    assert size == sum([os.path.getsize(x) for x in filelist])


def test_path_stat_gt0_plen(tdir):
    """Test path_stat function return piece length > 0."""
    _, _, piece_length = path_stat(tdir)
    assert piece_length >= MIN_BLOCK


def test_path_stat_base2_plen(tdir):
    """Test path_stat function return piece length is power of 2."""
    _, _, piece_length = path_stat(tdir)
    assert piece_length % MIN_BLOCK == 0


def test_path_stat_gtsize_plen(tdir):
    """Test path_stat function return size > piece length."""
    _, size, piece_length = path_stat(tdir)
    assert size > piece_length


def test_path_piece_length_pow2(tdir):
    """Test path_piece_length for file return piece_length is power of 2."""
    result = path_piece_length(tdir)
    assert result % MIN_BLOCK == 0


def test_path_piece_length_min(tdir):
    """Test path_piece_length for dir return piece_length is power of 2."""
    result = path_piece_length(tdir)
    assert result >= MIN_BLOCK


def test_path_piece_length_max(tdir):
    """Test path_piece_length for dir return piece_length < Maximum."""
    result = path_piece_length(tdir)
    assert result <= MAX_BLOCK


def test_encode(metadata):
    """Test Benencoder."""
    encoder = Benencoder(metadata)
    data = encoder.encode()
    assert data is not None


def test_encode_type(metadata):
    """Test Benencoder output type."""
    encoder = Benencoder(metadata)
    data = encoder.encode()
    assert isinstance(data, bytes)


def test_decode(bencode):
    """Test Bendecoder."""
    decoder = Bendecoder(bencode)
    data = decoder.decode()
    assert data is not None


def test_decode_type(bencode):
    """Test Bendecoder output type."""
    decoder = Bendecoder(bencode)
    data = decoder.decode()
    assert isinstance(data, dict)


def test_decode_type_info(bencode):
    """Test Benencoder output contents type."""
    decoder = Bendecoder(bencode)
    data = decoder.decode()
    assert "info" in data


def test_decode_type_announce(bencode):
    """Test Benencoder output contents."""
    decoder = Bendecoder(bencode)
    data = decoder.decode()
    assert "announce" in data


def test_decode_type_piecelength(bencode):
    """Test Bendecoder output contents."""
    decoder = Bendecoder(bencode)
    data = decoder.decode()
    assert "piece length" in data


def test_decode_type_created_by(bencode):
    """Test Bendecoder output type."""
    decoder = Bendecoder(bencode)
    data = decoder.decode()
    assert "created by" in data
