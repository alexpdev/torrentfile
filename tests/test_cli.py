import pytest
import os
import shutil
from torrentfile import main
from torrentfile.exceptions import MissingPathError
from tests.context import testdir, testfile, ntempdir

"""
List of flags for the Command Line Interface.

Options = [
    "--source", "--comment", "--private",
    "--created-by", "--piece-length",
    ("--v2","-v"),
    ("--path", "-p"),
    ("-t", "-a",),
    ("-o", "--outfile",)]
"""

@pytest.fixture(scope="function")
def tmeta(ntempdir):
    args = ["--path", ntempdir, "-t", "http://anounce.com/announce",
            "--source", "Alpha","--piece-length", str(2**20),
            "--private","--comment","some comment"]
    outfile, meta = main(args)
    yield meta
    os.remove(outfile)
    if os.path.exists(ntempdir):
        shutil.rmtree(ntempdir)

def test_cli_args_dir(testdir):
    args = ["--path", testdir]
    outfile, _ = main(args)
    assert os.path.exists(outfile)
    os.remove(outfile)


def test_cli_args_dir_v2(testdir):
    args = ["--path", testdir, "--v2"]
    outfile, _ = main(args)
    assert os.path.exists(outfile)
    os.remove(outfile)


def test_cli_args_file(testfile):
    args = ["--path", testfile]
    outfile, _ = main(args)
    assert os.path.exists(outfile)
    os.remove(outfile)


def test_cli_args_file_v2(testfile):
    args = ["--path", testfile, "--v2"]
    outfile, _ = main(args)
    assert os.path.exists(outfile)
    os.remove(outfile)


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

def test_cli_meta_source_dir(tmeta):
    assert "source" in tmeta["info"]
    assert tmeta["info"]["source"] == "Alpha"


fixtures_ = [testdir, testfile, ntempdir]
