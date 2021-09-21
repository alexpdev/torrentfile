import os
import sys
import pytest
from torrentfile.torrentfile import main
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
    folder = tempdir()
    yield folder
    rmpath(folder)


@pytest.fixture(scope="module")
def testdir():
    folder = tempdir()
    return folder


@pytest.fixture(scope="module")
def tfile():
    fd = tempfile()
    yield fd
    rmpath(fd)


@pytest.fixture(scope="function")
def tmeta(testdir):
    args = [
        "-t",
        "http://anounce.com/announce",
        "--source",
        "Alpha",
        "--piece-length",
        str(2 ** 20),
        "--private",
        "--comment",
        "some comment",
        "--path",
        testdir
    ]
    sys.argv = [sys.argv[0]] + args
    parser = main()
    yield parser
    rmpath(parser.outfile)
    rmpath(testdir)


def test_cli_args_dir(tdir):
    args = ["--path",tdir]
    sys.argv = [sys.argv[0]] + args
    parser = main()
    assert os.path.exists(parser.outfile)
    os.remove(parser.outfile)


def test_cli_args_dir_v2(tdir):
    args = ["-p", tdir, "--v2"]
    sys.argv = [sys.argv[0]] + args
    parser = main()
    assert os.path.exists(parser.outfile)
    os.remove(parser.outfile)


def test_cli_args_file(tfile):
    args = ["--path", tfile]
    sys.argv = [sys.argv[0]] + args
    parser = main()
    assert os.path.exists(parser.outfile)
    os.remove(parser.outfile)


def test_cli_args_file_v2(tfile):
    args = ["-p", tfile, "--v2"]
    sys.argv = [sys.argv[0]] + args
    parser = main()
    assert os.path.exists(parser.outfile)
    os.remove(parser.outfile)


def test_cli_no_args():
    try:
        sys.argv = [sys.argv[0]]
        assert main()
    except MissingPathError:
        assert True


def test_cli_no_args_v2():
    args = ["--v2"]
    try:
        sys.argv = [sys.argv[0]] + args
        assert main()
    except MissingPathError:
        assert True

