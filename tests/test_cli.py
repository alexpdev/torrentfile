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

from tests.context import parameters, rmpath
from torrentfile import main


@pytest.fixture(scope="module", params=parameters())
def tdir(request):
    """Generate temp testing directory."""
    directory = request.param()
    yield directory
    rmpath(directory)


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


def test_cli_no_args():
    """Test CLI script with specific arguments."""
    sys.argv = [sys.argv[0]]
    try:
        main()
    except SystemExit:
        assert True  # nosec


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
        str(2 ** 15),
        "--private",
        "--source",
        "TRACKER",
    ]
    parser = main()
    assert os.path.exists(parser.outfile)  # nosec
    rmpath(parser.outfile)


def test_cli_with_all_args_v2(tdir):
    """Test CLI script with specific arguments."""
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
    parser = main()
    assert os.path.exists(parser.outfile)  # nosec
    rmpath(parser.outfile)


def test_cli_with_all_args_v3(tdir):
    """Test CLI script with specific arguments."""
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
    parser = main()
    assert os.path.exists(parser.outfile)  # nosec
    rmpath(parser.outfile)
