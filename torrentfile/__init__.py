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

import argparse
import os
import sys

from torrentfile import feeder, metafile, utils
from torrentfile.feeder import Feeder
from torrentfile.metafile import TorrentFile
from torrentfile.utils import (Benencoder, get_file_list, get_piece_length,
                               path_size, path_stat)
from torrentfile.window import Application, Window, start

__version__ = "1.2.0"
__author__ = "alexpdev"
__cwd__ = os.getcwd()
__platform__ = sys.platform

__all__ = [
    "main",
    "CLI",
    "cli_parse",
    "__version__",
    "__author__",
    "Application",
    "Window",
    "TorrentFile",
    "Benencoder",
    "Feeder",
    "path_stat",
    "path_size",
    "get_file_list",
    "get_piece_length",
    "utils",
    "metafile",
    "feeder",
]


class CLI:

    kwargs = {
        "announce": None,
        "comment": None,
        "created_by": None,
        "path": None,
        "piece_length": None,
        "private": None,
        "source": None,
    }

    @classmethod
    def compile_kwargs(cls):
        for k, v in cls.__dict__.items():
            if k in cls.kwargs:
                if isinstance(v, bool):
                    v = 1 if v else 0
                cls.kwargs[k] = v
                print(k, v)
        return cls.kwargs

    @classmethod
    def create_torrentfile(cls):
        kwargs = cls.kwargs
        torrentfile = TorrentFile(**kwargs)
        torrentfile.assemble()
        if cls.outfile:
            torrentfile.write(cls.outfile)
        else:
            torrentfile.write()


def cli_parse(args):
    parser = argparse.ArgumentParser(
        prog="torrentfile", description="Torrentfile Interface", prefix_chars="-"
    )
    parser.add_argument(
        "--created-by",
        action="store",
        dest="created_by",
        metavar="X",
        help="leave out unless specifically instructed otherwise",
    )
    parser.add_argument(
        "--comment",
        action="store",
        dest="comment",
        metavar="X",
        help="include comment in binary data",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        action="store",
        help="save output to file.",
        dest="outfile",
        metavar="~/X.torrent",
    )
    parser.add_argument(
        "-p",
        "--path",
        action="store",
        required=True,
        help="Path to file of directory of torrent contents.",
        dest="path",
        metavar="~/X",
    )
    parser.add_argument(
        "--piece-length",
        action="store",
        help="Size of individual pieces of the torrent data.",
        dest="piece_length",
        metavar="X",
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="torrent will be distributed on a private tracker",
        dest="private",
    )
    parser.add_argument(
        "--source",
        action="store",
        dest="source",
        metavar="X",
        help="leave out unless specifically instructed otherwise",
    )
    parser.add_argument(
        "-t",
        "-a",
        action="extend",
        required=True,
        nargs="+",
        help="trackers/announce urls",
        dest="announce",
        metavar="url",
    )
    parser.parse_args(args=args[1:], namespace=CLI)
    CLI.compile_kwargs()
    CLI.create_torrentfile()


def main():
    args = sys.argv
    try:
        if sys.stdin.isatty():
            cli_parse(args)
        else:
            start()
    except:
        start()

if __name__ == "__main__":
    main()
