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

import os
import random
import shutil
import string

TD = os.path.abspath(os.path.dirname(__file__))


class Flags:

    """Dummy class for testing purposes.

    Minimally emulates the argparse.Namespace class.

    Attributes:
        path(`any`, Optional): path to contents of torrent
        announce(`any`, Optional): url for tracker.
        piece_length(`any`, Optional): size of each transmitable content
        source(`any`, Optional): leave blank.
        private(`any`, Optional): for private tracker?
        outfile(`any`, Optional): path to write .torrent file.
        created_by(`any`, Optional): program creator... leave blank.
        comment(`any`, Optional): any comment.
        v2(`any`, Optional): Meta Version 2 .torrentfile
        announce_list(`any`, Optional): additional trackers
    """

    def __init__(self, **kwargs):
        """Dummy class for testing purposes.

        Kwargs:
            path(`any`): path to contents of torrent
            announce(`any`, Optional): url for tracker.
            piece_length(`any`, Optional): size of each transmitable content
            source(`any`, Optional): leave blank.
            private(`any`, Optional): for private tracker?
            outfile(`any`, Optional): path to write .torrent file.
            created_by(`any`, Optional): program creator... leave blank.
            comment(`any`, Optional): any comment.
            v2(`any`, Optional): Meta Version 2 .torrentfile
            announce_list(`any`, Optional): additional trackers
        """
        self.path = None
        self.announce = None
        self.piece_length = None
        self.source = None
        self.private = None
        self.outfile = None
        self.created_by = None
        self.comment = None
        self.v2 = None
        self.announce_list = None
        for k,v in kwargs.items():
            if hasattr(self, k):
                self.__setattr__(k, v)


def seq():
    text = string.printable + string.punctuation + string.hexdigits
    random.shuffle(list(text))
    return "".join(text)


def fill_file(path, exp):
    bits = seq().encode("utf8")
    filesize = l = len(bits)
    with open(path, "wb") as fd:
        while filesize < 2 ** exp:
            fd.write(bits)
            filesize += l


def fill_folder(folder):
    files = {"file1.bin": 25, "file2.bin": 26}
    for k, v in files.items():
        path = os.path.join(folder, k)
        fill_file(path, v)


def rmpath(path):
    if not os.path.exists(path):
        return
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)

def rmpaths(paths):
    for path in paths:
        rmpath(path)

def tempdir():
    tdir = os.path.join(TD, "tempdir")
    tdir_1 = os.path.join(tdir, "directory1")
    for folder in [tdir, tdir_1]:
        rmpath(folder)
        os.mkdir(folder)
        fill_folder(folder)
    return tdir


def tempfile():
    path = os.path.join(TD, "tempfile.bin")
    fill_file(path, 28)
    return path

def sizedfile(num=28):
    path = os.path.join(TD, "tempfile.bin")
    fill_file(path, num)
    return path
