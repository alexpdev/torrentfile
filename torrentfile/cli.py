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

import logging
import sys
from argparse import ArgumentParser

import torrentfile

from .hybrid import TorrentFileHybrid
from .metafile import TorrentFile
from .metafile2 import TorrentFileV2
from .progress import CheckerClass


def main_script(args=None):
    """Initialize Command Line Interface for torrentfile.

    Args:
        args (`list`, default=None): Commandline arguments.
    """
    if not args:
        args = sys.argv[1:]

    desc = ("Create or Re-Check Bittorrent meta files for "
            "Bittorrent v1, v2 or v1, v2 combo Hybrids.")
    parser = ArgumentParser("torrentfile", description=desc, prefix_chars="-")
    # formatter_class=RawTextHelpFormatter

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"torrentfile v{torrentfile.__version__}",
        help="show program version and exit",
    )

    parser.add_argument(
        "-a",
        "--announce",
        action="store",
        dest="announce",
        metavar="<url>",
        default="",
        help="announce url for Bittorrent tracker",
    )

    parser.add_argument(
        "--announce-list",
        dest="announce_list",
        nargs="+",
        metavar="<url>",
        help="additional tracker announce URLs",
    )

    parser.add_argument(
        "-c",
        "--comment",
        action="store",
        dest="comment",
        metavar="<comment>",
        help="include a comment in file metadata",
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        dest="debug",
        help="activate debug mode"
    )

    parser.add_argument(
        "-m",
        "--meta-version",
        default="1",
        choices=["1", "2", "3"],
        action="store",
        dest="meta_version",
        metavar="<meta version>",
        help="""
        Specify the Bittorrent Protocol and formatting version for
        .torrent file.
        Options = 1, 2 or 3.
        (1) = Bittorrent v1;. (Default)
        (2) = Bittorrent v2.
        (3) = Bittorrent v1 & v2 hybrid.
        """,
    )

    parser.add_argument(
        "-o",
        "--out",
        action="store",
        dest="outfile",
        metavar="<out>",
        help="output path for files created",
    )

    parser.add_argument(
        "-p",
        "--piece-length",
        action="store",
        dest="piece_length",
        metavar="<piece length>",
        help="""
        Piece size used by Bittorrent transfer.
        Acceptable values include numbers 14-35, will be treated as the
        exponent for 2^n power, or any power of 2 integer in 16KB-16MB.
        e.g. [--piece-length 14] is the same as [--piece-length  16384]
        If this option isn't triggered, the program will calculate an
        appropriate value automatically.
        """,
    )

    parser.add_argument(
        "--private",
        action="store_true",
        dest="private",
        help="create .torrent file for private tracker",
    )

    parser.add_argument(
        "-r",
        "--re-check",
        dest="checker",
        metavar="<path>",
        nargs=2,
        help="""
        Activate Re-Check mode.
        Arguements:
        1) Absolute or relative path to The path to a ".torrent" file.
        2) Absolute or relative path to Torrent Contents
        When option is active, all other options are ignored (except debug).
        This option triggers a re-check of torrent contents on disk compared
        to contents detailed in .torrent file. Outputs the percentage
        downloaded or available in terminal.
        """
    )

    parser.add_argument(
        "-s",
        "--source",
        action="store",
        dest="source",
        metavar="<source>",
        help="specify source",
    )

    parser.add_argument(
        "path",
        action="store",
        default="",
        nargs="?",
        metavar="<path>",
        help="abs. or rel. path to content for creating .torrent file",
    )

    if not args:
        args = ["-h"]
    flags = parser.parse_args(args)

    if flags.debug or flags.checker:
        level = logging.DEBUG
    else:
        level = logging.WARNING

    logging.basicConfig(level=level, format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S')
    if flags.checker:
        checker = CheckerClass(flags.checker[0], flags.checker[1])
        return checker.result

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
    main_script()


if __name__ == "__main__":
    main()   # pragma: no cover
