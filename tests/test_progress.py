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
"""Testing functions for the progress module."""

import os
import sys

import pytest

from tests.context import parameters, rmpath, rmpaths, sizedfile, tempdir3
from torrentfile import TorrentFile, TorrentFileHybrid, TorrentFileV2, main
from torrentfile.progress import CheckerClass

TESTS = os.environ["TESTDIR"]


def mktorrent(args, v=None):
    """Compile bittorrent meta file."""
    if v == 3:
        torrent = TorrentFileHybrid(**args)
    elif v == 2:
        torrent = TorrentFileV2(**args)
    else:
        torrent = TorrentFile(**args)
    base = os.path.basename(args['path'])
    name = f"{base}.{v}.torrent"
    outfile = os.path.join(TESTS, name)
    torrent.write(outfile)
    return outfile


@pytest.fixture(scope="module")
def t3dir():
    """Fixture for TempDir3 configuration."""
    tempdir = tempdir3()
    yield tempdir
    rmpath(tempdir)


@pytest.fixture(params=[25, 26, 27, 28])
def tfile(request):
    """Temporary testing files for testing torrent validation."""
    tempfile = sizedfile(num=request.param)
    yield tempfile
    rmpath(tempfile)


@pytest.mark.parametrize("path", parameters())
@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_class(path, version):
    """Test Checker Class against meta files."""
    path = path()
    args = {"path": path, "announce": "https://announce.com/announce"}
    outfile = mktorrent(args, v=version)
    checker = CheckerClass(outfile, path)
    assert checker.result == "100"  # nosec
    rmpaths([outfile, path])


@pytest.mark.parametrize("path", parameters())
@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_first_piece(path, version):
    """Test Checker Class when first piece is slightly alterred."""
    path = path()
    args = {"path": path, "announce": "https://announce.com/announce"}
    outfile = mktorrent(args, v=version)

    def change(path):
        if os.path.isfile(path):
            data = open(path, "rb").read()
            new = b'some_different_bytes_to_swap'
            data = new + data[len(new):]
            open(path, "wb").write(data)
        elif os.path.isdir(path):
            for item in os.listdir(path):
                change(os.path.join(path, item))
    change(path)
    checker = CheckerClass(outfile, path)
    assert int(checker.result) != 100  # nosec
    rmpaths([outfile, path])


@pytest.mark.parametrize("path", parameters())
@pytest.mark.parametrize("version", [1, 2, 3])
def test_metafile_checker(path, version):
    """Test metadata checker class."""
    path = path()
    args = {"announce": "announce", "path": path, "private": 1}
    outfile = mktorrent(args, v=version)
    checker = CheckerClass(outfile, path)
    assert checker.result == "100"  # nosec
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_partial_metafiles(t3dir, version):
    """Test Checker with data that is expected to be incomplete."""
    args = {"announce": "announce", "path": t3dir, "private": 1}
    outfile = mktorrent(args, v=version)

    def shortenfile(path):
        with open(path, "rb") as bfile:
            data = bfile.read()
        with open(path, "wb") as bfile:
            bfile.write(data[:-2**12])
    for item in os.listdir(t3dir):
        full = os.path.join(t3dir, item)
        if os.path.isfile(full):
            shortenfile(full)
    TESTS = os.path.dirname(t3dir)
    checker = CheckerClass(outfile, TESTS)
    assert checker.result != "100"  # nosec
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_no_content(t3dir, version):
    """Test Checker class with directory that points to nothing."""
    args = {"announce": "announce", "path": t3dir, "private": 1}
    outfile = mktorrent(args, v=version)
    CheckerClass.register_hooks(lambda *x: print(x), lambda *x: print(x))
    checker = CheckerClass(outfile, t3dir)
    assert checker.result is not None   # nosec
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_cli_args(t3dir, version):
    """Test exclusive Checker Mode CLI."""
    args = {"announce": "announce", "path": t3dir, "private": 1}
    outfile = mktorrent(args, v=version)
    sys.argv[1:] = ["--checker", outfile, t3dir]
    output = main()
    assert output == "100"   # nosec
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_parent_dir(t3dir, version):
    """Test providing the parent directory for torrent checking feature."""
    args = {"announce": "announce", "path": t3dir, "private": 1}
    outfile = mktorrent(args, v=version)
    checker = CheckerClass(outfile, os.path.dirname(t3dir))
    assert checker.result == "100"  # nosec


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_with_file(version, tfile):
    """Test checker with single file torrent."""
    args = {"announce": "announce", "path": tfile, "private": 1}
    outfile = mktorrent(args, v=version)
    checker = CheckerClass(outfile, tfile)
    assert checker.result == "100"  # nosec
