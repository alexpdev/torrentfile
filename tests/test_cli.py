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

import pytest

from tests.context import rmpath, tempdir1, tempfile
from torrentfile import main

# from torrentfile.utils import MissingPathError

# List of flags for the Command Line Interface.

# Options = [
#     "--source", "--comment", "--private",
#     "--piece-length",
#     ("--v2","-v"),
#     ("--path", "-p"),
#     ("-t", "-a",),
#     ("-o", "--outfile",)]


@pytest.fixture(scope="module")
def tdir():
    """Generate temp testing directory."""
    directory = tempdir1()
    yield directory
    rmpath(directory)


@pytest.fixture(scope="module")
def tfile():
    """Generate temp testing file."""
    temp = tempfile()
    yield temp
    rmpath(temp)


def test_cli_args_dir(tdir):
    """Test CLI script with specific arguments."""
    args = [tdir]
    sys.argv = [sys.argv[0]] + args
    parser = main()
    assert os.path.exists(parser.outfile)  # nosec
    rmpath(parser.outfile)


def test_cli_args_dir_v2(tdir):
    """Test CLI script with specific arguments."""
    args = [tdir, "--meta-version", "2"]
    sys.argv = [sys.argv[0]] + args
    parser = main()
    assert os.path.exists(parser.outfile)  # nosec
    rmpath(parser.outfile)


def test_cli_args_dir_v3(tdir):
    """Test CLI script with specific arguments."""
    args = [tdir, "--meta-version", "3"]
    sys.argv = [sys.argv[0]] + args
    parser = main()
    assert os.path.exists(parser.outfile)  # nosec
    rmpath(parser.outfile)


def test_cli_args_file(tfile):
    """Test CLI script with specific arguments."""
    args = [tfile]
    sys.argv = [sys.argv[0]] + args
    parser = main()
    assert os.path.exists(parser.outfile)  # nosec
    rmpath(parser.outfile)


def test_cli_args_file_v2(tfile):
    """Test CLI script with specific arguments."""
    args = [tfile, "--meta-version", "2"]
    sys.argv = [sys.argv[0]] + args
    parser = main()
    assert os.path.exists(parser.outfile)  # nosec
    rmpath(parser.outfile)


def test_cli_args_file_v3(tfile):
    """Test CLI script with specific arguments."""
    args = [tfile, "--meta-version", "3"]
    sys.argv = [sys.argv[0]] + args
    parser = main()
    assert os.path.exists(parser.outfile)  # nosec
    rmpath(parser.outfile)


def test_cli_no_args():
    """Test CLI script with specific arguments."""
    sys.argv = [sys.argv[0]]
    try:
        main()
    except SystemExit:
        assert True  # nosec


def test_cli_with_all_args_file(tfile):
    """Test CLI script with specific arguments."""
    sys.argv = [
        "torrentfile",
        tfile,
        "--meta-version",
        "2",
        "-a",
        "https://tracker-url.com/announce",
        "--comment",
        "some comment",
        "--piece-length",
        str(2 ** 14),
        "--private",
        "--source",
        "TRACKER",
    ]
    parser = main()
    assert os.path.exists(parser.outfile)  # nosec
    rmpath(parser.outfile)


def test_cli_with_all_args_dir(tdir):
    """Test CLI script with specific arguments."""
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
        str(2 ** 14),
        "--private",
        "--source",
        "TRACKER",
    ]
    parser = main()
    assert os.path.exists(parser.outfile)  # nosec
    rmpath(parser.outfile)
