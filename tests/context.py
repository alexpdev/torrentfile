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


def rmpath(path):
    """Recursively remove path."""
    if not os.path.exists(path):
        return
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)


def rmpaths(paths):
    """Recursively remove all paths."""
    for path in paths:
        rmpath(path)


def datadir(func):
    """Create testing directory for all temp and testfiles created."""
    def wrapper(*args, **kwargs):
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
    """Multi nested directories with multi files in each dir."""
    root = os.path.join(TESTDIR, "RootFolder")
    dir1 = os.path.join(root, "directory1")
    dir2 = os.path.join(root, "directory2")
    dirs = [root, dir1, dir2]
    file1 = (os.path.join(dir1, "file1"), 14)
    file2 = (os.path.join(dir1, "file2"), 16)
    file3 = (os.path.join(dir2, "file3"), 18)
    file4 = (os.path.join(dir2, "file4"), 20)
    files = [file1, file2, file3, file4]
    fill_folder(dirs, files)
    return root


@datadir
def tempdir2():
    """Single file file structure with nested directories."""
    root = os.path.join(TESTDIR, "RootFolder")
    dir1 = os.path.join(root, "directory1")
    dirs = [root, dir1]
    file1 = (os.path.join(dir1, "file1"), 28)
    files = [file1]
    fill_folder(dirs, files)
    return root


@datadir
def tempdir3():
    """Multi file directory structure with small file sizes."""
    root = os.path.join(TESTDIR, "RootFolder")
    dirs = [root]
    file1 = (os.path.join(root, "file1"), 14)
    file2 = (os.path.join(root, "file2"), 14)
    file3 = (os.path.join(root, "file3"), 14)
    file4 = (os.path.join(root, "file4"), 14)
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


@atexit.register
def teardown():
    """Teardown function for the end of testing."""
    rmpath(TESTDIR)


# def tempdir():
#     """Generate temporary directory filled with meaningless data."""
#     datadir()
#     tdir = os.path.join(TESTDIR, "tempdir")
#     tdir_1 = os.path.join(tdir, "directory1")
#     for folder in [tdir, tdir_1]:
#         rmpath(folder)
#         os.mkdir(folder)
#         fill_folder(folder)
#     return tdir
