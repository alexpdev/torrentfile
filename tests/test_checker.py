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
"""Context Functions used throughout testing suite."""

import os
import sys

import pytest

from tests.context import parameters, rmpath, sizedfile, tempdir3
from torrentfile import (Checker, TorrentFile, TorrentFileHybrid,
                         TorrentFileV2, main)


@pytest.fixture(scope="module", params=parameters())
def testdir(request):
    """Return temp directory."""
    val = request.param()
    yield val
    rmpath(val)


def mktorrent(args, v=None):
    """Creating different versions of .torrent files for testing."""
    if v == 3:
        torrent = TorrentFileHybrid(**args)
    elif v == 2:
        torrent = TorrentFileV2(**args)
    else:
        torrent = TorrentFile(**args)
    return torrent.write()


@pytest.fixture(scope="module")
def tdir3():
    """Fixture for TempDir3 configuration."""
    tempdir = tempdir3()
    yield tempdir
    rmpath(tempdir)


@pytest.fixture(scope="module", params=[25, 26, 27, 28])
def tfile(request):
    """Temporary testing files for testing torrent validation."""
    tempfile = sizedfile(num=request.param)
    yield tempfile
    rmpath(tempfile)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_metafile_checker(testdir, version):
    """Test metadata checker class."""
    args = {"announce": "announce", "path": testdir, "private": 1}
    outfile, _ = mktorrent(args, v=version)
    checker = Checker(outfile, testdir)
    status = checker.check()
    assert status == "100%"  # nosec
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_partial_metafiles(tdir3, version):
    """Test Checker with data that is expected to be incomplete."""
    args = {"announce": "announce", "path": tdir3, "private": 1}
    outfile, _ = mktorrent(args, v=version)

    def shortenfile(path):
        with open(path, "rb") as bfile:
            data = bfile.read()
        with open(path, "wb") as bfile:
            bfile.write(data[:-2**12])
    for item in os.listdir(tdir3):
        full = os.path.join(tdir3, item)
        if os.path.isfile(full):
            shortenfile(full)
    testdir = os.path.dirname(tdir3)
    checker = Checker(outfile, testdir)
    status = checker.check()
    assert status != "100%"  # nosec
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_no_content(tdir3, version):
    """Test Checker class with directory that points to nothing."""
    args = {"announce": "announce", "path": tdir3, "private": 1}
    outfile, _ = mktorrent(args, v=version)
    Checker.add_callback(lambda x: sys.stdout.write(x.upper()))
    checker = Checker(outfile, "assets")
    assert checker.check() is not None   # nosec
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_cli_args(tdir3, version):
    """Test exclusive Checker Mode CLI."""
    args = {"announce": "announce", "path": tdir3, "private": 1}
    outfile, _ = mktorrent(args, v=version)
    sys.argv[1:] = ["--checker", outfile, tdir3]
    output = main()
    assert output == "100%"   # nosec
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_parent_dir(tdir3, version):
    """Test providing the parent directory for torrent checking feature."""
    args = {"announce": "announce", "path": tdir3, "private": 1}
    outfile, _ = mktorrent(args, v=version)
    checker = Checker(outfile, os.path.dirname(tdir3))
    status = checker.check()
    assert status == "100%"  # nosec


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_with_file(version, tfile):
    """Test checker with single file torrent."""
    args = {"announce": "announce", "path": tfile, "private": 1}
    outfile, _ = mktorrent(args, v=version)
    checker = Checker(outfile, tfile)
    status = checker.check()
    assert status == "100%"  # nosec
