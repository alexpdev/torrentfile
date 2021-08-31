import pytest
import os
from tests.context import testfile, testdir
from torrentfile import main
from torrentfile.exceptions import MissingPathError

"""
Options = [
    "--created-by",
    "--comment",
    "-o",
    "--path",
    "--piece-length",
    "--private",
    "--source",
    "-t",
    "--v2",
]
"""


def test_cli_args_dir(testdir):
    args = ["--path", testdir]
    outfile, _ = main(args)
    assert os.path.exists(outfile)
    os.remove("testdir.torrent")

def test_cli_args_dir_v2(testdir):
    args = ["--path", testdir, "--v2"]
    outfile, _ = main(args)
    assert os.path.exists(outfile)
    os.remove("testdir.torrent")

def test_cli_args_file(testfile):
    args = ["--path", testfile]
    outfile, _ = main(args)
    assert os.path.exists(outfile)
    os.remove("testfile.bin.torrent")

def test_cli_args_file_v2(testfile):
    args = ["--path", testfile, "--v2"]
    outfile, _ = main(args)
    assert os.path.exists(outfile)
    os.remove("testfile.bin.torrent")

def test_cli_no_args():
    args = []
    try:
        assert main(args)
    except MissingPathError:
        assert True

def test_cli_no_args_v2():
    args = ["--v2"]
    try:
        assert main(args)
    except MissingPathError:
        assert True
