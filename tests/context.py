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

import atexit
import os
import random
import shutil
import string

TD = os.path.abspath(os.path.dirname(__file__))
TESTDIR = os.path.join(TD, "TESTDIR")
os.environ["TESTDIR"] = TESTDIR


def rmpath(paths):
    """Recursively remove path."""
    if isinstance(paths, (os.PathLike, str)):
        paths = [paths]
    for path in paths:
        if os.path.exists(path):
            if os.path.isdir(path):
                try:
                    shutil.rmtree(path)
                except PermissionError:  # pragma: no cover
                    return      # pragma: no cover
            else:
                os.remove(path)
        assert not os.path.exists(path)   # nosec


def datadir(func):
    """Create testing directory for all temp and testfiles created."""
    def wrapper(*args, **kwargs):
        """Wrap function for datadir."""
        if not os.path.exists(TESTDIR):
            os.mkdir(TESTDIR)
        return func(*args, **kwargs)
    return wrapper


def seq():
    """Generate random sequence of characters."""
    text = string.printable + string.punctuation + string.hexdigits
    random.shuffle(list(text))
    return "".join(text)


def fill_file(path, exp):
    """Fill file with random bytes."""
    bits = seq().encode("utf8")
    bitlen = len(bits)
    filesize = 0
    with open(path, "wb") as fd:
        while filesize + bitlen < 2 ** exp:
            fd.write(bits)
            filesize += bitlen
        diff = 2 ** exp - filesize
        fd.write(bits[: diff + 1])


def fill_folder(dirs, files):
    """Fill testing files and folders with random data.

    Args:
        dirs (`list`): a list of directories.
        files (`list`): a list of files.

    Returns:
        path (`str`): Path to root testing folder.
    """
    for folder in dirs:
        if os.path.exists(folder):
            rmpath(folder)
        os.mkdir(folder)
    for path, exp in files:
        fill_file(path, exp)


@datadir
def tempdir1():
    """Configure multi nested directories with multi files in each dir."""
    root = os.path.join(TESTDIR, "RootFolder1")
    dir1 = os.path.join(root, "directory1")
    dir2 = os.path.join(root, "directory2")
    dirs = [root, dir1, dir2]
    file1 = (os.path.join(dir1, "file1"), 16)
    file2 = (os.path.join(dir1, "file2"), 22)
    file3 = (os.path.join(dir2, "file3"), 23)
    file4 = (os.path.join(dir2, "file4"), 20)
    files = [file1, file2, file3, file4]
    fill_folder(dirs, files)
    return root


@datadir
def tempdir2():
    """Configure single file file structure with nested directories."""
    root = os.path.join(TESTDIR, "RootFolder2")
    dir1 = os.path.join(root, "directory1")
    dirs = [root, dir1]
    file1 = (os.path.join(dir1, "file1"), 21)
    files = [file1]
    fill_folder(dirs, files)
    return root


@datadir
def tempdir3():
    """Configure multi file directory structure with small file sizes."""
    root = os.path.join(TESTDIR, "RootFolder3")
    dirs = [root]
    file1 = (os.path.join(root, "file1"), 14)
    file2 = (os.path.join(root, "file2"), 16)
    file3 = (os.path.join(root, "file3"), 16)
    file4 = (os.path.join(root, "file4"), 14)
    files = [file1, file2, file3, file4]
    fill_folder(dirs, files)
    return root


@datadir
def tempdir4():
    """Configure multi file directory structure with small file sizes."""
    root = os.path.join(TESTDIR, "RootFolder4")
    dir1 = os.path.join(root, "directory1")
    dir2 = os.path.join(root, "directory2")
    dirs = [root, dir1, dir2]
    file1 = (os.path.join(dir1, "file1"), 22)
    file2 = (os.path.join(dir1, "file2"), 25)
    file3 = (os.path.join(dir2, "file3"), 21)
    file4 = (os.path.join(dir2, "file4"), 24)
    files = [file1, file2, file3, file4]
    fill_folder(dirs, files)
    return root


@datadir
def tempfile():
    """Generate temporary file filled with meaningless data."""
    path = os.path.join(TESTDIR, "tempfile.bin")
    fill_folder([], [(path, 23)])
    return path


@datadir
def sizedfile(num=28):
    """Generate a specifically sized file with meaningless data."""
    path = os.path.join(TESTDIR, "tempfile.bin")
    fill_file(path, num)
    return path


def parameters():
    """Return a list of all tempdir configurations."""
    return [tempdir1, tempdir2, tempdir3, tempdir4]


@atexit.register
def teardown():
    """Teardown function for the end of testing."""
    rmpath(TESTDIR)
