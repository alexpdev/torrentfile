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
from argparse import ArgumentParser, HelpFormatter

import torrentfile

from .hybrid import TorrentFileHybrid
from .metafile import TorrentFile
from .metafile2 import TorrentFileV2
from .progress import CheckerClass


class HelpFormat(HelpFormatter):
    """Formatting class for help tips provided by the CLI.

    Args:
        prog (`str`): Name of the program.
        width (`int`): Max width of help message output.
        max_help_positions (`int`): max length until line wrap.
    """

    def __init__(self, prog, width=80, max_help_pos=45):
        """Construct HelpFormat class."""
        super().__init__(prog, width=width, max_help_position=max_help_pos)

    def _split_lines(self, text, _):
        """Split multiline help messages and remove indentation."""
        lines = text.split("\n")
        return [line.strip() for line in lines if line]


def main_script(args=None):
    """Initialize Command Line Interface for torrentfile.

    Args:
        args (`list`, default=None): Commandline arguments.
    """
    if not args:
        args = sys.argv[1:]

    desc = ("Create or Re-Check Bittorrent meta files for "
            "Bittorrent v1, v2 or v1, v2 combo Hybrids.")

    parser = ArgumentParser("torrentfile", description=desc,
                            prefix_chars="-", formatter_class=HelpFormat)

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"torrentfile v{torrentfile.__version__}",
        help="show program version and exit"
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        dest="debug",
        help="output debug information"
    )

    parser.add_argument(
        "-p",
        "--private",
        action="store_true",
        dest="private",
        help="create .torrent file for private tracker",
    )

    parser.add_argument(
        "-s",
        "--source",
        action="store",
        dest="source",
        metavar="<source>",
        help="specify source"
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
        "-a",
        "--announce",
        action="store",
        dest="announce",
        metavar="<url>",
        nargs="+",
        default="",
        help="1 or more announce url's for Bittorrent tracker"
    )

    parser.add_argument(
        "-o",
        "--out",
        action="store",
        dest="outfile",
        metavar="<path>",
        help="output path for created .torrent file",
    )

    parser.add_argument(
        "--meta-version",
        default="1",
        choices=["1", "2", "3"],
        action="store",
        dest="meta_version",
        metavar="<int>",
        help="""
        .torrent file version.
        Options = 1, 2 or 3.
        (1) = Bittorrent v1;. (Default)
        (2) = Bittorrent v2.
        (3) = Bittorrent v1 & v2 hybrid.
        """,
    )

    parser.add_argument(
        "-l",
        "--piece-length",
        action="store",
        dest="piece_length",
        metavar="<int>",
        help="""
        piece size used by Bittorrent transfer protocol.
        Acceptable values include numbers 14-35, will be treated as the
        exponent for 2^n power, or any power of 2 integer in 16KB-16MB.
        e.g. `--piece-length 14` is the same as `--piece-length  16384`
        If this option flag is not used, the program will calculate an
        appropriate value automatically.
        """,
    )

    parser.add_argument(
        "-r",
        "--re-check",
        dest="checker",
        metavar="<.torrent>",
        help="""
        <.torrent> is the path to a .torrent meta file.
        Check <content> data integrity with <.torrent> file.
        When this option is active, all other options are ignored (except -d).
        """
    )

    parser.add_argument(
        "content",
        action="store",
        metavar="<content>",
        help="path to .torrent file content"
    )

    if not args:
        args = ["-h"]
    flags = parser.parse_args(args)

    if flags.debug:
        level = logging.DEBUG
    elif flags.checker:
        level = logging.INFO
    else:
        level = logging.WARNING

    logging.basicConfig(level=level, format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S')
    if flags.checker:
        metafile = flags.checker
        content = flags.content
        checker = CheckerClass(metafile, content)
        result = checker.result
        sys.stdout.write(str(result))
        return result

    kwargs = {
        "path": flags.content,
        "announce": flags.announce,
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
