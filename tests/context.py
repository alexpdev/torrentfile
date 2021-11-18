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
from datetime import datetime
from pathlib import Path

from torrentfile import TorrentFile, TorrentFileHybrid, TorrentFileV2

TD = os.path.dirname(os.path.abspath(__file__))


def structs():
    """Temporary directory structures for testing."""
    return [[
        "Root1/dir1/file1",
        "Root1/dir1/file2",
        "Root1/dir2/file3",
        "Root1/dir2/file4",
        "Root1/file5",
    ], [
        "Root2/file1",
        "Root2/file2",
        "Root2/file3",
        "Root2/file4",
    ], [
        "Root3/dir1/dir2/file1",
        "Root3/dir1/file2",
        "Root3/dir3/dir4/file3",
        "Root3/file4",
    ]]


def rootwrap(func):
    """Wrap to ensure root folder exists."""
    def wrapper(*args, **kwargs):
        """Execute function wrapper internal func."""
        if not os.path.exists(Temp.root):
            os.mkdir(Temp.root)
        return func(*args, **kwargs)
    return wrapper


class Temp:
    """Temp class for holding context variables."""

    root = os.path.join(TD, "TESTDIR")
    seq = string.printable + string.whitespace + string.hexdigits
    structs = structs()
    dirs = []
    procedures = [TorrentFile, TorrentFileV2, TorrentFileHybrid]

    @classmethod
    def rmdirs(cls):
        """Remove created directories on completion."""
        size = len(cls.dirs) - 1
        while size >= 0:
            if rmpath(cls.dirs[size]):
                del cls.dirs[size]
            size -= 1


def tstamp():
    """Return timestamp corresponding to now."""
    return str(datetime.timestamp(datetime.now()))


def rmpath(paths):
    """Recursively remove path."""
    if isinstance(paths, (os.PathLike, str)):
        paths = [paths]
    no_errors = True
    for path in [p for p in paths if os.path.exists(p)]:
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        except PermissionError:  # pragma: no cover
            no_errors = False
            continue
    return no_errors


@rootwrap
def testfile(path=None, exp=21):
    """Test filling a temporary file."""
    if not path:
        path = os.path.join(Temp.root, f"file{str(tstamp())}")
    seq = Temp.seq.encode("utf-8") * 8
    with open(path, "bw") as binfile:
        size = 2**exp
        while size > 0:
            binfile.write(seq)
            size -= len(seq)
    assert os.path.exists(path)  # nosec
    return path


@rootwrap
def mkdirs(path):
    """Make partials for long directory hiearchy."""
    parts = Path(path).parts
    base = Path(Temp.root) / parts[0]
    for i in range(1, len(parts)):
        if not os.path.exists(base):
            os.mkdir(base)
            Temp.dirs.append(base)
        base = base / parts[i]
    return base


@rootwrap
def build(struct, start=14, stop=25):
    """Build the file structure provided with sizes."""
    top = Path(struct[0]).parts[0]
    root = os.path.join(Temp.root, top)
    for txt in struct:
        path = mkdirs(txt)
        size = random.randint(start, stop)  # nosec
        testfile(path=path, exp=size)
    return root


@atexit.register
def teardown():
    """Teardown function for the end of testing."""
    rmpath(Temp.root)
