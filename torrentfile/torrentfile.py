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

"""
Main script entrypoint for creating .torrent files.

This module provides the primary command line argument parser for
the torrentfile package.  The main_script function is automatically
invoked when called from command line, and parses accompanying arguments.

Functions:
    main_script: process command line arguments and run program.
"""

import sys
from argparse import ArgumentParser
import torrentfile
from .exceptions import MissingPathError
from .metafile import TorrentFile
from .metafile2 import TorrentFileV2
from .hybrid import TorrentFileHybrid


def main_script(args=None):
    """Initialize Command Line Interface for torrentfile.

    usage: torrentfile --path /path/to/content [-o /path/to/output.torrent]
           [--piece-length n] [--private] [-t https://tracker.url/announce]
           [--v2] [--source x] [--announce-list tracker.url2 tracker.url3]
           [-h]
    """
    if not args:
        args = sys.argv[1:]

    usage = """torrentfile --path </path/to/content> [-o <output/path.torrent>]
            [--piece-length <n>] [--private] [-a https://tracker.url/announce]
            [--meta-version <n>] [--source <x>] [--announce-list <url2> <...>]"""

    d = "Create .torrent files for Bittorrent v1 or v2."
    parser = ArgumentParser(
        "torrentfile", description=d, prefix_chars="-", usage=usage, allow_abbrev=False
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"torrentfile v{torrentfile.__version__}",
        help="show program version and exit\n",
    )

    parser.add_argument(
        "-p",
        "--path",
        action="store",
        dest="path",
        metavar="<path>",
        help="(required) path to torrent content",
    )

    parser.add_argument(
        "-a",
        "--announce",
        action="store",
        dest="announce",
        metavar="<url>",
        help="Primary tracker url.",
    )

    parser.add_argument(
        "--piece-length",
        action="store",
        dest="piece_length",
        metavar="<n>",
        help="Transmit size for pieces of torrent content.",
    )

    parser.add_argument(
        "--private",
        action="store_true",
        dest="private",
        help="For torrents distributed on private trackers.",
    )

    parser.add_argument(
        "-o",
        "--out",
        action="store",
        help="Specify path for .torrent file.",
        dest="outfile",
        metavar="<path>",
    )

    parser.add_argument(
        "--meta-version",
        choices=["1", "2", "3"],
        action="store",
        help=(
            "Specify the version of torrent metafile to create."
            "1 = v1, 2 = v2, 3 = 1 & 2 Hybrid"
        ),
        default="1",
        dest="meta_version",
        metavar="<n>",
    )

    parser.add_argument(
        "--comment",
        action="store",
        dest="comment",
        metavar="<comment>",
        help="Include a comment in file metadata.",
    )

    parser.add_argument(
        "--source",
        action="store",
        dest="source",
        metavar="<source>",
        help="ignore unless instructed otherwise",
    )

    parser.add_argument(
        "--announce-list",
        action="extend",
        dest="announce_list",
        nargs="+",
        metavar="[<url>, ...]",
        help="Additional tracker url's",
    )
    if not args:
        args = ["-h"]

    flags = parser.parse_args(args)

    if not flags.path:
        raise MissingPathError(flags)

    kwargs = {
        "path": flags.path,
        "announce": flags.announce,
        "announce_list": flags.announce_list,
        "piece_length": flags.piece_length,
        "source": flags.source,
        "private": flags.private,
        "outfile": flags.outfile,
        "comment": flags.comment,
    }
    print(flags)
    if flags.meta_version == "2":
        torrent = TorrentFileV2(**kwargs)
    elif flags.meta_version == "1":
        torrent = TorrentFile(**kwargs)
    elif flags.meta_version == "3":
        torrent = TorrentFileHybrid(**kwargs)
    else:
        raise MissingPathError(flags)
    torrent.assemble()
    outfile, meta = torrent.write()
    parser.kwargs = kwargs
    parser.meta = meta
    parser.outfile = outfile
    return parser


def main():
    """Initiate main function for CLI script."""
    return main_script()


if __name__ == "__main__":
    main()
