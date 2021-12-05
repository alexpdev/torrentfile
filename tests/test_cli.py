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

from tests.context import Temp, build, rmpath
from torrentfile import main, main_script


@pytest.mark.parametrize("struct", Temp.structs)
@pytest.mark.parametrize("start", list(range(14, 19)))
@pytest.mark.parametrize("stop", list(range(19, 23)))
def test_cli_args_dir(struct, start, stop):
    """Test CLI script with only path as arguement."""
    args = [build(struct, start, stop)]
    sys.argv = [sys.argv[0]] + args
    parser = main_script()
    assert os.path.exists(parser.outfile)  # nosec
    rmpath(parser.outfile)


@pytest.mark.parametrize("struct", Temp.structs)
@pytest.mark.parametrize("start", list(range(14, 19)))
@pytest.mark.parametrize("stop", list(range(19, 23)))
def test_cli_args_dir_v2(struct, start, stop):
    """Test CLI script with minimal arguments v2."""
    tdir = build(struct, start, stop)
    args = [tdir, "--meta-version", "2"]
    sys.argv = [sys.argv[0]] + args
    parser = main_script()
    assert os.path.exists(parser.outfile)  # nosec
    rmpath(parser.outfile)


@pytest.mark.parametrize("struct", Temp.structs)
@pytest.mark.parametrize("start", list(range(14, 19)))
@pytest.mark.parametrize("stop", list(range(19, 23)))
def test_cli_args_dir_v3(struct, start, stop):
    """Test CLI script with minimal arguments v3."""
    tdir = build(struct, start, stop)
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


@pytest.mark.parametrize("struct", Temp.structs)
@pytest.mark.parametrize("start", list(range(14, 19)))
@pytest.mark.parametrize("stop", list(range(19, 23)))
def test_cli_with_all_args_dir(struct, start, stop):
    """Test CLI script with other specific arguments v3."""
    tdir = build(struct, start, stop)
    sys.argv = [
        "torrentfile",
        tdir,
        "--meta-version",
        "3",
        "-t",
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


@pytest.mark.parametrize("struct", Temp.structs)
@pytest.mark.parametrize("start", list(range(14, 19)))
@pytest.mark.parametrize("stop", list(range(19, 23)))
def test_cli_with_all_args_v2(struct, start, stop):
    """Test CLI script with all arguments v2."""
    tdir = build(struct, start, stop)
    sys.argv = [
        "torrentfile",
        tdir,
        "--meta-version",
        "2",
        "-d",
        "-t",
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


@pytest.mark.parametrize("struct", Temp.structs)
@pytest.mark.parametrize("start", list(range(14, 19)))
@pytest.mark.parametrize("stop", list(range(19, 23)))
def test_cli_with_all_args_v3(struct, start, stop):
    """Test CLI script with all arguments v3."""
    tdir = build(struct, start, stop)
    sys.argv = [
        "torrentfile",
        tdir,
        "--meta-version",
        "3",
        "-d",
        "-t",
        "https://tracker-url.com/announce",
        "--align-pieces",
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
@pytest.mark.parametrize("field", ["announce", "announce list",
                                   "piece layers", "created by",
                                   "info", "creation date", "url-list"])
@pytest.mark.parametrize("struct", Temp.structs)
def test_cli_meta_output_v2_3(struct, field, version):
    """Test CLI output torrentfile meta dict fields v2 and hybrid."""
    tdir = build(struct)
    sys.argv = [
        "torrentfile",
        tdir,
        "--meta-version",
        str(version),
        "-d",
        "-t",
        "https://tracker-url.com/announce",
        "https://tracker2-url.com/announce",
        "https://tracker3-url.com/announce",
        "-w",
        "http://someurl.com/link",
        "http://other.net/link",
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
                                   "meta version"])
@pytest.mark.parametrize("struct", Temp.structs)
def test_cli_info_output_v2_3(struct, field, version):
    """Test CLI output file info dict meta versions 2 & 3."""
    tdir = build(struct)
    sys.argv = [
        "torrentfile",
        tdir,
        "--meta-version",
        str(version),
        "-d",
        "-t",
        "https://tracker-url.com/announce",
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
                                   "comment", "private", "source"])
@pytest.mark.parametrize("struct", Temp.structs)
def test_cli_info_output_v1(struct, field):
    """Test CLI output files contents with specific arguments v1."""
    tdir = build(struct)
    sys.argv = [
        "torrentfile",
        tdir,
        "-d",
        "--align-pieces",
        "-t",
        "https://tracker-url.com/announce",
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
                                   "creation date", "info",
                                   "announce list", "url-list"])
@pytest.mark.parametrize("struct", Temp.structs)
def test_cli_meta_output_v1(struct, field):
    """Test CLI output v1 file meta dict specific arguments."""
    tdir = build(struct)
    sys.argv = [
        "torrentfile",
        tdir,
        "-d",
        "-t",
        "https://tracker-url.com/announce",
        "https://tracker2-url.com/announce",
        "https://tracker3-url.com/announce",
        "-w",
        "http://urlforfile.site/link",
        "http://some.thing/link",
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
