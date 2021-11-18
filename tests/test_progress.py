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

from tests.context import Temp, build, rmpath, testfile
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
    outfile = os.path.join(Temp.root, name)
    torrent.write(outfile)
    return outfile


@pytest.mark.parametrize("struct", Temp.structs)
@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_class(struct, version):
    """Test Checker Class against meta files."""
    path = build(struct)
    args = {"path": path, "announce": "https://announce.com/announce"}
    outfile = mktorrent(args, v=version)
    checker = CheckerClass(outfile, path)
    assert checker.result == "100"  # nosec
    rmpath([outfile, path])


@pytest.mark.parametrize("struct", Temp.structs)
@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_first_piece(struct, version):
    """Test Checker Class when first piece is slightly alterred."""
    path = build(struct)
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


@pytest.mark.parametrize("struct", Temp.structs)
@pytest.mark.parametrize("version", [1, 2, 3])
def test_metafile_checker(struct, version):
    """Test metadata checker class."""
    path = build(struct)
    args = {"announce": "announce", "path": path, "private": 1}
    outfile = mktorrent(args, v=version)
    checker = CheckerClass(outfile, path)
    assert checker.result == "100"  # nosec
    rmpath([outfile, path])


@pytest.mark.parametrize("version", [1, 2, 3])
@pytest.mark.parametrize("struct", Temp.structs)
def test_partial_metafiles(struct, version):
    """Test Checker with data that is expected to be incomplete."""
    t3dir = build(struct)
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
@pytest.mark.parametrize("struct", Temp.structs)
def test_checker_no_content(struct, version):
    """Test Checker class with directory that points to nothing."""
    t3dir = build(struct)
    args = {"announce": "announce", "path": t3dir, "private": 1}
    outfile = mktorrent(args, v=version)
    CheckerClass.register_callback(lambda *x: print(x))
    checker = CheckerClass(outfile, t3dir)
    assert checker.result == "100"   # nosec
    rmpath(outfile)


@pytest.mark.parametrize("version", [1, 2, 3])
@pytest.mark.parametrize("struct", Temp.structs)
def test_checker_cli_args(struct, version):
    """Test exclusive Checker Mode CLI."""
    t3dir = build(struct)
    args = {"announce": "announce", "path": t3dir, "private": 1}
    outfile = mktorrent(args, v=version)
    sys.argv[1:] = ["--re-check", outfile, t3dir]
    output = main()
    assert output == "100"   # nosec
    rmpath(outfile)
    Temp.rmdirs()


@pytest.mark.parametrize("version", [1, 2, 3])
@pytest.mark.parametrize("struct", Temp.structs)
def test_checker_parent_dir(struct, version):
    """Test providing the parent directory for torrent checking feature."""
    t3dir = build(struct)
    args = {"announce": "announce", "path": t3dir, "private": 1}
    outfile = mktorrent(args, v=version)
    checker = CheckerClass(outfile, os.path.dirname(t3dir))
    assert checker.result == "100"  # nosec
    rmpath(outfile)
    Temp.rmdirs()


@pytest.mark.parametrize("size", list(range(14, 26)))
@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_with_file(version, size):
    """Test checker with single file torrent."""
    tfile = testfile(exp=size)
    args = {"announce": "announce", "path": tfile, "private": 1}
    outfile = mktorrent(args, v=version)
    checker = CheckerClass(outfile, tfile)
    assert checker.result == "100"  # nosec
    rmpath(outfile)


def test_checker_no_meta_file():
    """Test Checker when incorrect metafile is provided."""
    try:
        CheckerClass("peaches", "$")
    except FileNotFoundError:
        assert True   # nosec


@pytest.mark.parametrize("struct", Temp.structs)
def test_checker_no_root_dir(struct):
    """Test Checker when incorrect root directory is provided."""
    tdir = build(struct)
    args = {"announce": "announce", "path": tdir, "private": 1}
    outfile = mktorrent(args, v=1)
    try:
        CheckerClass(outfile, "peaches")
    except FileNotFoundError:
        assert True   # nosec
    rmpath(outfile)


@pytest.mark.parametrize("struct", Temp.structs)
def test_checker_wrong_root_dir(struct):
    """Test Checker when incorrect root directory is provided."""
    tdir = build(struct)
    args = {"announce": "announce", "path": tdir, "private": 1}
    path = Path(tdir)
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


@pytest.fixture
def struct1():
    """Return single struct list."""
    path = build(Temp.structs[1])
    return path


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_class_missing(version, struct1):
    """Test Checker class when files are missing from contents."""
    path = struct1
    args = {"announce": "announce", "path": path,
            "private": 1, "piece_length": 2**16}
    outfile = mktorrent(args, v=version)
    rmpath(os.path.join(path, "file1"))
    rmpath(os.path.join(path, "file3"))
    checker = CheckerClass(outfile, path)
    assert int(checker.result) < 100   # nosec


@pytest.mark.parametrize("struct", Temp.structs)
@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_class_allfiles(version, struct):
    """Test Checker class when all files are missing from contents."""
    path = Path(build(struct))
    args = {"announce": "announce", "path": path,
            "private": 1, "piece_length": 2**16}
    outfile = mktorrent(args, v=version)

    def traverse(path):
        """Traverse internal subdirectories."""
        if path.is_file():
            rmpath(path)
        elif path.is_dir():
            for item in path.iterdir():
                traverse(item)

    traverse(path)
    checker = CheckerClass(outfile, path)
    assert int(checker.result) < 100   # nosec
    rmpath(outfile)
    Temp.rmdirs()


@pytest.mark.parametrize("version", [1, 2, 3])
@pytest.mark.parametrize("struct", Temp.structs)
def test_checker_class_allpaths(version, struct):
    """Test Checker class when all files are missing from contents."""
    path = Path(build(struct))
    args = {"announce": "announce", "path": path,
            "private": 1, "piece_length": 2**16}
    outfile = mktorrent(args, v=version)
    for item in path.iterdir():
        rmpath(item)
    checker = CheckerClass(outfile, path)
    assert int(checker.result) < 100   # nosec


@pytest.mark.parametrize("version", [1, 2, 3])
def test_checker_class_half_file(version):
    """Test Checker class with half size single file."""
    path = testfile(exp=25)
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
    path = testfile(exp=20)
    args = {"announce": "announce", "path": path,
            "private": 1, "piece_length": 2**14}
    outfile = mktorrent(args, v=version)
    checker = CheckerClass(outfile, path)
    result = checker.result
    assert checker.result == result   # nosec
    rmpath(outfile)
