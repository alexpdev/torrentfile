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
from pathlib import Path

import pytest

from tests.context import parameters, rmpath, sizedfile, tempdir3, tempdir4
from torrentfile import TorrentFile, TorrentFileHybrid, TorrentFileV2
from torrentfile.cli import main_script as main
from torrentfile.progress import CheckerClass


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
    outfile = os.path.join(os.environ["TESTDIR"], name)
    torrent.write(outfile)
    return outfile


@pytest.fixture(scope="module")
def t3dir():
    """Fixture for TempDir3 configuration."""
    tempdir = tempdir3()
    yield tempdir
    rmpath(tempdir)


@pytest.fixture
def t4dir():
    """Fixture for TempDir4 configuration."""
    tempdir = tempdir4()
    yield tempdir
    rmpath(tempdir)


@pytest.fixture(params=[25, 26, 27, 24])
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
    rmpath([outfile, path])


@pytest.mark.parametrize("path", parameters())
@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_first_piece(path, version):
    """Test Checker Class when first piece is slightly alterred."""
    path = path()
    args = {"path": path, "announce": "https://announce.com/announce"}
    outfile = mktorrent(args, v=version)

    def change(path):
        """Change some bytes in file."""
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
    rmpath([outfile, path])


@pytest.mark.parametrize("path", parameters())
@pytest.mark.parametrize("version", [1, 2, 3])
def test_metafile_checker(path, version):
    """Test metadata checker class."""
    path = path()
    args = {"announce": "announce", "path": path, "private": 1}
    outfile = mktorrent(args, v=version)
    checker = CheckerClass(outfile, path)
    assert checker.result == "100"  # nosec
    rmpath([outfile, path])


@pytest.mark.parametrize("version", [1, 2, 3])
def test_partial_metafiles(t3dir, version):
    """Test Checker with data that is expected to be incomplete."""
    args = {"announce": "announce", "path": t3dir, "private": 1}
    outfile = mktorrent(args, v=version)

    def shortenfile(path):
        """Shorten a few files for testing purposes."""
        with open(path, "rb") as bfile:
            data = bfile.read()
        with open(path, "wb") as bfile:
            bfile.write(data[:-2**12])
    for item in os.listdir(t3dir):
        full = os.path.join(t3dir, item)
        if os.path.isfile(full):
            shortenfile(full)

    testdir = os.path.dirname(t3dir)
    checker = CheckerClass(outfile, testdir)
    assert checker.result != "100"  # nosec
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_no_content(t3dir, version):
    """Test Checker class with directory that points to nothing."""
    args = {"announce": "announce", "path": t3dir, "private": 1}
    outfile = mktorrent(args, v=version)
    CheckerClass.register_callback(lambda *x: print(x))
    checker = CheckerClass(outfile, t3dir)
    assert checker.result == "100"   # nosec
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_cli_args(t3dir, version):
    """Test exclusive Checker Mode CLI."""
    args = {"announce": "announce", "path": t3dir, "private": 1}
    outfile = mktorrent(args, v=version)
    sys.argv[1:] = ["--re-check", outfile, t3dir]
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
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_with_file(version, tfile):
    """Test checker with single file torrent."""
    args = {"announce": "announce", "path": tfile, "private": 1}
    outfile = mktorrent(args, v=version)
    checker = CheckerClass(outfile, tfile)
    assert checker.result == "100"  # nosec
    rmpath(outfile)


def test_checker_no_meta_file(t3dir):
    """Test Checker when incorrect metafile is provided."""
    try:
        CheckerClass("peaches", t3dir)
    except FileNotFoundError:
        assert True   # nosec


def test_checker_no_root_dir(t3dir):
    """Test Checker when incorrect root directory is provided."""
    args = {"announce": "announce", "path": t3dir, "private": 1}
    outfile = mktorrent(args, v=1)
    try:
        CheckerClass(outfile, "peaches")
    except FileNotFoundError:
        assert True   # nosec
    rmpath(outfile)


def test_checker_wrong_root_dir(t3dir):
    """Test Checker when incorrect root directory is provided."""
    args = {"announce": "announce", "path": t3dir, "private": 1}
    path = Path(t3dir)
    newpath = path.parent / (path.name + "FAKE")
    os.mkdir(newpath)
    newpath.touch(newpath / "file1")
    outfile = mktorrent(args, v=1)
    try:
        CheckerClass(outfile, str(newpath))
    except FileNotFoundError:
        assert True   # nosec
    rmpath(outfile)
    rmpath(newpath)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_class_missing(version):
    """Test Checker class when files are missing from contents."""
    path = tempdir3()
    args = {"announce": "announce", "path": path,
            "private": 1, "piece_length": 2**16}
    outfile = mktorrent(args, v=version)
    rmpath(os.path.join(path, "file1"))
    rmpath(os.path.join(path, "file3"))
    checker = CheckerClass(outfile, path)
    assert int(checker.result) < 100   # nosec
    rmpath(outfile)
    rmpath(path)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_class_half_file(version):
    """Test Checker class with half size single file."""
    path = sizedfile(25)
    args = {"announce": "announce", "path": path,
            "private": 1, "piece_length": 2**15}
    outfile = mktorrent(args, v=version)
    half = int((2**25) / 2)
    barr = bytearray(half)
    with open(path, "rb") as content:
        content.readinto(barr)
    with open(path, "wb") as content:
        content.write(barr)
    checker = CheckerClass(outfile, path)
    assert int(checker.result) < 100  # nosec


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_result_property(version):
    """Test Checker class with half size single file."""
    path = sizedfile(20)
    args = {"announce": "announce", "path": path,
            "private": 1, "piece_length": 2**14}
    outfile = mktorrent(args, v=version)
    checker = CheckerClass(outfile, path)
    result = checker.result
    assert checker.result == result   # nosec
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_missing_files2(version, t4dir):
    """Testing Meta Version 2 & hybrid checkerclass when missing files."""
    args = {"announce": "announce", "path": t4dir,
            "private": 1, "piece_length": 2**14}
    outfile = mktorrent(args, v=version)
    paths = [os.path.join(t4dir, "directory1", "file2"),
             os.path.join(t4dir, "directory2", "file4")]
    rmpath(paths)
    checker = CheckerClass(outfile, t4dir)
    assert int(checker.result) < 100  # nosec
    rmpath(outfile)
