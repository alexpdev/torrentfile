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
"""Test CLI script functionality."""

import os
import sys

import pyben
import pytest

from tests.context import parameters, rmpath
from torrentfile import main, main_script


@pytest.fixture(scope="module", params=parameters())
def tdir(request):
    """Generate temp testing directory."""
    directory = request.param()
    yield directory
    rmpath(directory)


def test_cli_args_dir(tdir):
    """Test CLI script with only path as arguement."""
    args = [tdir]
    sys.argv = [sys.argv[0]] + args
    parser = main_script()
    assert os.path.exists(parser.outfile)  # nosec
    rmpath(parser.outfile)


def test_cli_args_dir_v2(tdir):
    """Test CLI script with minimal arguments v2."""
    args = [tdir, "--meta-version", "2"]
    sys.argv = [sys.argv[0]] + args
    parser = main_script()
    assert os.path.exists(parser.outfile)  # nosec
    rmpath(parser.outfile)


def test_cli_args_dir_v3(tdir):
    """Test CLI script with minimal arguments v3."""
    args = [tdir, "--meta-version", "3"]
    sys.argv = [sys.argv[0]] + args
    parser = main_script()
    assert os.path.exists(parser.outfile)  # nosec
    rmpath(parser.outfile)


def test_cli_no_args():
    """Test CLI script with no arguments."""
    sys.argv = [sys.argv[0]]
    try:
        main()
    except SystemExit:
        assert True  # nosec


def test_cli_with_all_args_dir(tdir):
    """Test CLI script with other specific arguments v3."""
    sys.argv = [
        "torrentfile",
        tdir,
        "--meta-version",
        "3",
        "-a",
        "https://tracker-url.com/announce",
        "--comment",
        "some comment",
        "--piece-length",
        str(2 ** 15),
        "--private",
        "--source",
        "TRACKER",
    ]
    parser = main_script()
    assert os.path.exists(parser.outfile)  # nosec
    rmpath(parser.outfile)


def test_cli_with_all_args_v2(tdir):
    """Test CLI script with all arguments v2."""
    sys.argv = [
        "torrentfile",
        tdir,
        "--meta-version",
        "2",
        "-d",
        "-a",
        "https://tracker-url.com/announce",
        "--comment",
        "some comment",
        "--piece-length",
        str(2 ** 16),
        "--private",
        "--source",
        "TRACKER",
    ]
    parser = main_script()
    assert os.path.exists(parser.outfile)  # nosec
    rmpath(parser.outfile)


def test_cli_with_all_args_v3(tdir):
    """Test CLI script with all arguments v3."""
    sys.argv = [
        "torrentfile",
        tdir,
        "--meta-version",
        "3",
        "-d",
        "-a",
        "https://tracker-url.com/announce",
        "--comment",
        "some comment",
        "--piece-length",
        str(2 ** 16),
        "--private",
        "--source",
        "TRACKER",
    ]
    parser = main_script()
    assert os.path.exists(parser.outfile)  # nosec
    rmpath(parser.outfile)


@pytest.mark.parametrize("version", [2, 3])
@pytest.mark.parametrize("field", ["announce", "piece layers", "info",
                                   "created by", "creation date"])
def test_cli_meta_output_v2_3(tdir, field, version):
    """Test CLI output torrentfile meta dict fields v2 and hybrid."""
    sys.argv = [
        "torrentfile",
        tdir,
        "--meta-version",
        str(version),
        "-d",
        "-a",
        "https://tracker-url.com/announce",
        "--announce-list",
        "https://tracker2-url.com/announce",
        "https://tracker3-url.com/announce",
        "--comment",
        "some comment",
        "--piece-length",
        str(2 ** 16),
        "--private",
        "--source",
        "TRACKER",
    ]
    parser = main_script()
    meta = pyben.load(parser.outfile)
    assert field in meta    # nosec
    rmpath(parser.outfile)


@pytest.mark.parametrize("version", [2, 3])
@pytest.mark.parametrize("field", ["piece length", "name", "file tree",
                                   "comment", "private", "source",
                                   "announce list", "meta version"])
def test_cli_info_output_v2_3(tdir, field, version):
    """Test CLI output file info dict meta versions 2 & 3."""
    sys.argv = [
        "torrentfile",
        tdir,
        "--meta-version",
        str(version),
        "-d",
        "-a",
        "https://tracker-url.com/announce",
        "--announce-list",
        "https://tracker2-url.com/announce",
        "https://tracker3-url.com/announce",
        "--comment",
        "some comment",
        "--piece-length",
        str(2 ** 16),
        "--private",
        "--source",
        "TRACKER",
    ]
    parser = main_script()
    meta = pyben.load(parser.outfile)
    assert field in meta["info"]   # nosec
    rmpath(parser.outfile)


@pytest.mark.parametrize("field", ["piece length", "name", "pieces",
                                   "comment", "private", "source",
                                   "announce list"])
def test_cli_info_output_v1(tdir, field):
    """Test CLI output files contents with specific arguments v1."""
    sys.argv = [
        "torrentfile",
        tdir,
        "-d",
        "-a",
        "https://tracker-url.com/announce",
        "--announce-list",
        "https://tracker2-url.com/announce",
        "https://tracker3-url.com/announce",
        "--comment",
        "some comment",
        "--piece-length",
        str(2 ** 16),
        "--private",
        "--source",
        "TRACKER",
    ]
    parser = main_script()
    meta = pyben.load(parser.outfile)
    assert field in meta["info"]  # nosec
    rmpath(parser.outfile)


@pytest.mark.parametrize("field", ["announce", "created by",
                                   "creation date", "info"])
def test_cli_meta_output_v1(tdir, field):
    """Test CLI output v1 file meta dict specific arguments."""
    sys.argv = [
        "torrentfile",
        tdir,
        "-d",
        "-a",
        "https://tracker-url.com/announce",
        "--announce-list",
        "https://tracker2-url.com/announce",
        "https://tracker3-url.com/announce",
        "--comment",
        "some comment",
        "--piece-length",
        str(2 ** 16),
        "--private",
        "--source",
        "TRACKER",
    ]
    parser = main_script()
    meta = pyben.load(parser.outfile)
    assert field in meta  # nosec
    rmpath(parser.outfile)
