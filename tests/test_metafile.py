import pytest
import os
from tests.context import testfile, testdir
from torrentfile import main
from torrentfile.metafile import MissingPathError

"""
Options = [
    "--created-by",
    "--comment",
    "-o",
    "--path",
    "--piece-length",
    "--private",
    "--source",
    "-t"
]
"""


def test_cli_args_dir(testdir):
    args = ["--path", testdir]
    assert main(args) == True
    os.remove("testdir.torrent")


def test_cli_args_file(testfile):
    args = ["--path", testfile]
    assert main(args) == True
    os.remove("testfile.bin.torrent")
