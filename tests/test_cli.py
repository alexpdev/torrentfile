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
from torrentfile import main
from torrentfile.exceptions import MissingPathError
from tests.context import tempfile, tempdir, rmpath

# List of flags for the Command Line Interface.

# Options = [
#     "--source", "--comment", "--private",
#     "--created-by", "--piece-length",
#     ("--v2","-v"),
#     ("--path", "-p"),
#     ("-t", "-a",),
#     ("-o", "--outfile",)]


@pytest.fixture(scope="module")
def tdir():
    """Generate temporary directory."""
    folder = tempdir()
    yield folder
    rmpath(folder)


@pytest.fixture(scope="module")
def tfile():
    """Generate temporary file."""
    fd = tempfile()
    yield fd
    rmpath(fd)


def test_cli_args_dir(tdir):
    """Test CLI script with specific arguments."""
    args = ["--path", tdir]
    sys.argv = [sys.argv[0]] + args
    parser = main()
    assert os.path.exists(parser.outfile)
    os.remove(parser.outfile)


def test_cli_args_dir_v2(tdir):
    """Test CLI script with specific arguments."""
    args = ["-p", tdir, "--v2"]
    sys.argv = [sys.argv[0]] + args
    parser = main()
    assert os.path.exists(parser.outfile)
    os.remove(parser.outfile)


def test_cli_args_file(tfile):
    """Test CLI script with specific arguments."""
    args = ["--path", tfile]
    sys.argv = [sys.argv[0]] + args
    parser = main()
    assert os.path.exists(parser.outfile)
    os.remove(parser.outfile)


def test_cli_args_file_v2(tfile):
    """Test CLI script with specific arguments."""
    args = ["-p", tfile, "--v2"]
    sys.argv = [sys.argv[0]] + args
    parser = main()
    assert os.path.exists(parser.outfile)
    os.remove(parser.outfile)


def test_cli_no_args():
    """Test CLI script with specific arguments."""
    sys.argv = [sys.argv[0]]
    assert True


def test_cli_no_args_v2():
    """Test CLI script with specific arguments."""
    try:
        args = ["--v2"]
        sys.argv = [sys.argv[0]] + args
        assert main()
    except MissingPathError:
        assert True


def test_cli_with_all_args_file(tfile):
    """Test CLI script with specific arguments."""
    sys.argv = ["torrentfile", "-p", tfile, "--v2", "-a",
                "https://tracker-url.com/announce", "--comment",
                "some comment", "--piece-length", str(2**14), "--private",
                "--source", "TRACKER", "--created-by", "PROGGRAM"]
    parser = main()
    assert os.path.exists(parser.outfile)


def test_cli_with_all_args_dir(tdir):
    """Test CLI script with specific arguments."""
    sys.argv = (["torrentfile", "-p", tdir, "--v2", "-a",
                 "https://tracker-url.com/announce", "--comment",
                 "some comment", "--piece-length", str(2**14), "--private",
                 "--source", "TRACKER", "--created-by", "PROGGRAM"])
    parser = main()
    assert os.path.exists(parser.outfile)
