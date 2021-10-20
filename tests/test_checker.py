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

from tests.context import parameters, rmpath, tempdir3
from torrentfile import (Checker, TorrentFile, TorrentFileHybrid,
                         TorrentFileV2, main)


@pytest.fixture(scope="module", params=parameters())
def testdir(request):
    """Return temp directory."""
    return request.param()


def mktorrent(args, v=None):
    """Creating different versions of .torrent files for testing."""
    if v == 3:
        torrent = TorrentFileHybrid(**args)
    elif v == 2:
        torrent = TorrentFileV2(**args)
    else:
        torrent = TorrentFile(**args)
    torrent.assemble()
    return torrent.write()


@pytest.fixture(scope="module")
def tdir3():
    """Fixture for TempDir3 configuration."""
    tempdir = tempdir3()
    yield tempdir
    rmpath(tempdir)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_metafile_checker(testdir, version):
    """Test metadata checker class."""
    args = {"announce": "announce", "path": testdir, "private": 1}
    outfile, _ = mktorrent(args, v=version)
    checker = Checker(outfile, testdir)
    status = checker.check()
    assert status == "100%"  # nosec


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


def test_checker_no_content(tdir3):
    """Test Checker class with directory that points to nothing."""
    args = {"announce": "announce", "path": tdir3, "private": 1}
    outfile, _ = mktorrent(args, v=3)
    Checker.add_callback(lambda x: sys.stdout.write(x.upper()))
    checker = Checker(outfile, "assets")
    assert checker.check() is None   # nosec


def test_checker_cli_args(tdir3):
    """Test exclusive Checker Mode CLI."""
    args = {"announce": "announce", "path": tdir3, "private": 1}
    outfile, _ = mktorrent(args, v=3)
    sys.argv[1:] = ["--checker", outfile, tdir3]
    output = main()
    assert output == "100%"   # nosec
