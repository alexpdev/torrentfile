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

from tests import dir1, dir2, rmpath, tempfile
from torrentfile import TorrentFile, TorrentFileHybrid, TorrentFileV2
from torrentfile.cli import main_script as main
from torrentfile.recheck import Checker


def test_fixtures():
    """Test fixtures exist."""
    assert dir1
    assert dir2


def mktorrent(args, v=None):
    """Compile bittorrent meta file."""
    if v == 3:
        torrent = TorrentFileHybrid(**args)
    elif v == 2:
        torrent = TorrentFileV2(**args)
    else:
        torrent = TorrentFile(**args)
    outfile = str(args["path"]) + ".torrent"
    torrent.write(outfile)
    return outfile


@pytest.fixture
def dir3():
    """Test fixture for directory structure."""
    files = [
        "dir3/subdir1/file1.png",
        "dir3/subdir1/file2.mp4",
        "dir3/subdir2/file3.mp3",
        "dir3/subdir2/file4.zip",
        "dir3/file4.jpg",
    ]
    paths = []
    for i, path in enumerate(files):
        temps = tempfile(path=path, exp=15 + i)
        paths.append(temps)
    path = os.path.commonpath(paths)
    yield path
    rmpath(path)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_class(dir1, version):
    """Test Checker Class against meta files."""
    args = {"path": str(dir1), "announce": "https://announce.com/announce"}
    outfile = mktorrent(args, v=version)
    checker = Checker(outfile, dir1)
    assert checker.results() == 100
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
@pytest.mark.parametrize("piece_length", [2 ** i for i in range(14, 18)])
def test_checker_class_alt(dir3, version, piece_length):
    """Test Checker Class against meta files."""
    args = {
        "path": str(dir3),
        "announce": "https://announce.com/announce",
        "piece_length": piece_length,
    }
    outfile = mktorrent(args, v=version)
    checker = Checker(outfile, dir3)
    assert checker.results() == 100
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_first_piece(dir2, version):
    """Test Checker Class when first piece is slightly alterred."""
    path = str(dir2)
    args = {"path": path, "announce": "https://announce.com/announce"}
    outfile = mktorrent(args, v=version)

    def change(path):
        """Change some bytes in file."""
        if path.is_file():
            new = b"Something other than what was there before."
            with open(path, "rb") as bfile:
                data = bfile.read()
            content = b"".join([new, data[len(new) :]])
            with open(path, "wb") as bdoc:
                bdoc.write(content)
        elif path.is_dir():
            for item in path.iterdir():
                change(item)

    change(Path(path))
    checker = Checker(outfile, path)
    assert checker.results() != 100
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
@pytest.mark.parametrize("piece_length", [2 ** i for i in range(14, 18)])
def test_checker_first_piece_alt(dir3, version, piece_length):
    """Test Checker Class when first piece is slightly alterred."""
    path = str(dir3)
    args = {
        "path": path,
        "announce": "https://announce.com/announce",
        "piece_length": piece_length,
    }
    outfile = mktorrent(args, v=version)

    def change(path):
        """Change some bytes in file."""
        if os.path.isfile(path):
            with open(path, "rb") as bfile:
                data = bfile.read()
            new = b"some_other_bytes_to_use"
            new_len = len(new)
            with open(path, "wb") as wfile:
                wfile.write(new + data[new_len:])
        elif os.path.isdir(path):
            for item in os.listdir(path):
                change(os.path.join(path, item))

    change(path)
    checker = Checker(outfile, path)
    assert checker.results() != 100
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_metafile_checker(dir1, version):
    """Test metadata checker class."""
    path = str(dir1)
    args = {"announce": "announce", "path": path, "private": 1}
    outfile = mktorrent(args, v=version)
    checker = Checker(outfile, path)
    assert checker.results() == 100
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
@pytest.mark.parametrize("piece_length", [2 ** i for i in range(14, 18)])
def test_metafile_checker_alt(dir3, version, piece_length):
    """Test metadata checker class."""
    path = str(dir3)
    args = {
        "announce": "announce",
        "path": path,
        "private": 1,
        "piece_length": piece_length,
    }
    outfile = mktorrent(args, v=version)
    checker = Checker(outfile, path)
    assert checker.results() == 100
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_partial_metafiles(dir2, version):
    """Test Checker with data that is expected to be incomplete."""
    path = str(dir2)
    args = {"announce": "announce", "path": path, "private": 1}
    outfile = mktorrent(args, v=version)

    def shortenfile(path):
        """Shorten a few files for testing purposes."""
        with open(path, "rb") as bfile:
            data = bfile.read()
        with open(path, "wb") as bfile:
            bfile.write(data[: -(2 ** 10)])

    for item in os.listdir(path):
        full = os.path.join(path, item)
        if os.path.isfile(full):
            shortenfile(full)

    testdir = os.path.dirname(path)
    checker = Checker(outfile, testdir)
    assert checker.results() != 100
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_no_content(dir1, version):
    """Test Checker class with directory that points to nothing."""
    path = str(dir1)
    args = {"announce": "announce", "path": path, "private": 1}
    outfile = mktorrent(args, v=version)
    Checker.register_callback(lambda *x: print(x))
    checker = Checker(outfile, path)
    assert checker.results() == 100
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
@pytest.mark.parametrize("piece_length", [2 ** i for i in range(14, 18)])
def test_checker_no_content_alt(dir3, version, piece_length):
    """Test Checker class with directory that points to nothing."""
    path = str(dir3)
    args = {
        "announce": "announce",
        "path": path,
        "private": 1,
        "piece_length": piece_length,
    }
    outfile = mktorrent(args, v=version)
    Checker.register_callback(lambda *x: print(x))
    checker = Checker(outfile, path)
    assert checker.results() == 100
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_cli_args(dir1, version):
    """Test exclusive Checker Mode CLI."""
    path = str(dir1)
    args = {"announce": "announce", "path": path, "private": 1}
    outfile = mktorrent(args, v=version)
    sys.argv = ["torrentfile", "check", outfile, path]
    output = main()
    assert output == 100
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_parent_dir(dir1, version):
    """Test providing the parent directory for torrent checking feature."""
    path = str(dir1)
    args = {"announce": "announce", "path": path, "private": 1}
    outfile = mktorrent(args, v=version)
    checker = Checker(outfile, os.path.dirname(path))
    assert checker.results() == 100
    rmpath(outfile)


@pytest.mark.parametrize("size", list(range(14, 26)))
@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_with_file(version, size):
    """Test checker with single file torrent."""
    tfile = tempfile(exp=size)
    args = {"announce": "announce", "path": tfile, "private": 1}
    outfile = mktorrent(args, v=version)
    checker = Checker(outfile, tfile)
    assert checker.results() == 100
    rmpath(outfile)


def test_checker_no_meta_file():
    """Test Checker when incorrect metafile is provided."""
    try:
        Checker("peaches", "$")
    except FileNotFoundError:
        assert True


def test_checker_no_root_dir(dir1):
    """Test Checker when incorrect root directory is provided."""
    path = str(dir1)
    args = {"announce": "announce", "path": path, "private": 1}
    outfile = mktorrent(args, v=1)
    try:
        Checker(outfile, "peaches")
    except FileNotFoundError:
        assert True
    rmpath(outfile)


def test_checker_wrong_root_dir(dir2):
    """Test Checker when incorrect root directory is provided."""
    tdir = str(dir2)
    args = {"announce": "announce", "path": tdir, "private": 1}
    path = Path(tdir)
    newpath = path.parent / (path.name + "FAKE")
    os.mkdir(newpath)
    newpath.touch(newpath / "file1")
    outfile = mktorrent(args, v=1)
    try:
        Checker(outfile, str(newpath))
    except FileNotFoundError:
        assert True
    rmpath(outfile, newpath)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_missing(version, dir2):
    """Test Checker class when files are missing from contents."""
    path = str(dir2)
    args = {
        "announce": "announce",
        "path": path,
        "private": 1,
        "piece_length": 2 ** 16,
    }
    outfile = mktorrent(args, v=version)
    count = 0
    for fd in Path(path).iterdir():
        if fd.is_file() and count < 2:
            rmpath(fd)
    checker = Checker(outfile, path)
    assert int(checker.results()) < 100


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_class_allfiles(version, dir2):
    """Test Checker class when all files are missing from contents."""
    path = Path(str(dir2))
    args = {
        "announce": "announce",
        "path": path,
        "private": 1,
        "piece_length": 2 ** 16,
    }
    outfile = mktorrent(args, v=version)

    def traverse(path):
        """Traverse internal subdirectories."""
        if path.is_file():
            rmpath(path)
        elif path.is_dir():
            for item in path.iterdir():
                traverse(item)

    traverse(path)
    checker = Checker(outfile, path)
    assert int(checker.results()) < 100
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_class_allpaths(version, dir2):
    """Test Checker class when all files are missing from contents."""
    path = Path(str(dir2))
    args = {
        "announce": "announce",
        "path": path,
        "private": 1,
        "piece_length": 2 ** 16,
    }
    outfile = mktorrent(args, v=version)
    for item in path.iterdir():
        rmpath(item)
    checker = Checker(outfile, path)
    assert int(checker.results()) < 100


@pytest.mark.parametrize("version", [1, 2, 3])
@pytest.mark.parametrize("piece_length", [2 ** i for i in range(14, 19)])
@pytest.mark.parametrize("size", list(range(16, 22)))
def test_checker_class_half_file(version, piece_length, size):
    """Test Checker class with half size single file."""
    path = tempfile(exp=size)
    args = {
        "announce": "announce",
        "path": path,
        "private": 1,
        "piece_length": piece_length,
    }
    outfile = mktorrent(args, v=version)
    half = int((2 ** size) / 2)
    barr = bytearray(half)
    with open(path, "rb") as content:
        content.readinto(barr)
    with open(path, "wb") as content:
        content.write(barr)
    checker = Checker(outfile, path)
    assert int(checker.results()) < 100


@pytest.mark.parametrize("version", [1, 2, 3])
@pytest.mark.parametrize("piece_length", [2 ** i for i in range(14, 21)])
def test_checker_missing_singles(version, piece_length, dir3):
    """Test Checker class with half size single file."""
    path = str(dir3)
    args = {
        "announce": "announce",
        "path": path,
        "private": 1,
        "piece_length": piece_length,
    }
    outfile = mktorrent(args, v=version)
    for item in Path(path).iterdir():
        rmpath(item)
        break
    checker = Checker(outfile, path)
    assert int(checker.results()) < 100


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_result_property(version):
    """Test Checker class with half size single file."""
    path = tempfile(exp=20)
    args = {
        "announce": "announce",
        "path": path,
        "private": 1,
        "piece_length": 2 ** 14,
    }
    outfile = mktorrent(args, v=version)
    checker = Checker(outfile, path)
    result = checker.results()
    assert checker.results() == result
    rmpath(outfile)


def test_checker_simplest():
    """Test the simplest example."""
    path = tempfile(exp=14)
    args = {"path": path, "piece_length": 14}
    outfile = mktorrent(args, v=1)
    checker = Checker(outfile, path)
    assert checker.results() == 100
