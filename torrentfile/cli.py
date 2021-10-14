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
from argparse import ArgumentParser, RawTextHelpFormatter

import torrentfile

from .hybrid import TorrentFileHybrid
from .metafile import TorrentFile
from .metafile2 import TorrentFileV2


def main_script(args=None):
    """Initialize Command Line Interface for torrentfile.

    Args:
        args (`list`, default=None): Commandline arguments.

    usage: torrentfile --path /path/to/content [-o /path/to/output.torrent]
           [--piece-length n] [--private] [-t https://tracker.url/announce]
           [--v2] [--source x] [--announce-list tracker.url2 tracker.url3]
           [-h]
    """
    if not args:
        args = sys.argv[1:]

    usage = (
        """\t   torrentfile -v --version
           torrentfile -h --help
           torrentfile path [-o <dest>] [-a <url>] [--private]
           [--piece-length <n>] [--meta-version <n>] [--source <x>]
           [--announce-list <url2> <...>] [--comment <comment>]"""
    )

    desc = "Create Bittorrent meta files for Bittorrent v1 and v2."
    parser = ArgumentParser("torrentfile", description=desc, prefix_chars="-",
                            usage=usage, formatter_class=RawTextHelpFormatter,
                            exit_on_error=False)

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"torrentfile v{torrentfile.__version__}",
        help="\t\tShow program version and exit\n",
    )

    parser.add_argument(
        "path",
        action="store",
        help="\t\tPath to content source file or directory.",
        metavar="<path>",
    )

    parser.add_argument(
        "-a",
        "--announce",
        action="store",
        dest="announce",
        metavar="<url>",
        help="\t\tPrimary announce url for Bittorrent Tracker.",
        default="127.0.0.1"
    )

    parser.add_argument(
        "-p",
        "--piece-length",
        action="store",
        dest="piece_length",
        metavar="<val>",
        help="""
            \tIntiger piece length for content used by Bittorrent Protocol.
            \tAcceptable Input values include 14-35 which will be treated as
            \tan exponent for 2^n power. Otherwise the value must be a
            \tperfect power of 2 between 16KB and 16MB.
            \ti.e. [--piece-length 14] is the same as [--piece-length  16384]
            \tAlternatively, leave blank and let the program calulate the
            \tappropriate piece length.
            """,
    )

    parser.add_argument(
        "--private",
        action="store_true",
        dest="private",
        help="\t\tCreate file for use with private tracker.",
    )

    parser.add_argument(
        "-o",
        "--out",
        action="store",
        help="\t\tPath to the target destination for the output .torrent file.",
        dest="outfile",
        metavar="<dest>",
    )

    parser.add_argument(
        "--meta-version",
        default="1",
        choices=["1", "2", "3"],
        action="store",
        help=("""
            \tOptions = 1, 2 or 3.
            \t(1) = Bittorrent v1;. (Default)
            \t(2) = Bittorrent v2.
            \t(3) = Bittorrent v1 & v2 hybrid.
            \tSpecify the Bittorrent Protocol and
            \tformatting version for .torrent file.
        """),
        dest="meta_version",
        metavar="<n>",
    )

    parser.add_argument(
        "--comment",
        action="store",
        dest="comment",
        metavar="<text>",
        help="\t\tInclude a comment in file metadata.",
    )

    parser.add_argument(
        "--source",
        action="store",
        dest="source",
        metavar="<text>",
        help="\t\tSpecify source.",
    )

    parser.add_argument(
        "--announce-list",
        action="extend",
        dest="announce_list",
        nargs="+",
        metavar="<url>",
        help="\t\tAdditional tracker announce URLs.",
    )
    if not args:
        args = ["-h"]

    flags = parser.parse_args(args)

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

    if flags.meta_version == "2":
        torrent = TorrentFileV2(**kwargs)

    elif flags.meta_version == "3":
        torrent = TorrentFileHybrid(**kwargs)

    else:
        torrent = TorrentFile(**kwargs)

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
