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
Command Line Interface for TorrentFile project.

This module provides the primary command line argument parser for
the torrentfile package. The main_script function is automatically
invoked when called from command line, and parses accompanying arguments.

Functions:
    main_script: process command line arguments and run program.
"""

import logging
import sys
from argparse import ArgumentParser, HelpFormatter

import torrentfile
from torrentfile.edit import edit_torrent
from torrentfile.interactive import select_action
from torrentfile.recheck import Checker
from torrentfile.torrent import TorrentFile, TorrentFileHybrid, TorrentFileV2


class HelpFormat(HelpFormatter):
    """Formatting class for help tips provided by the CLI.

    Parameters
    ----------
    prog : `str`
        Name of the program.
    width : `int`
        Max width of help message output.
    max_help_positions : `int`
        max length until line wrap.
    """

    def __init__(self, prog: str, width=75, max_help_pos=40):
        """Construct HelpFormat class."""
        super().__init__(prog, width=width, max_help_position=max_help_pos)

    def _split_lines(self, text, _):
        """Split multiline help messages and remove indentation."""
        lines = text.split("\n")
        return [line.strip() for line in lines if line]


def main_script(args=None):
    """Initialize Command Line Interface for torrentfile.

    Parameters
    ----------
    args : `list`
        Commandline arguments. default=None
    """
    if not args:
        if sys.argv[1:]:
            args = sys.argv[1:]
        else:
            args = ["-h"]

    parser = ArgumentParser(
        "TorrentFile",
        description="""
        CLI Tool for creating, checking and editing Bittorrent meta files.
        Supports all meta file versions including hybrid files.
        """,
        prefix_chars="-",
        formatter_class=HelpFormat,
    )

    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        dest="interactive",
        help="select program options interactively",
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"torrentfile v{torrentfile.__version__}",
        help="show program version and exit",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="debug",
        help="output debug information",
    )

    subparsers = parser.add_subparsers(
        title="Commands",
        description="TorrentFile sub-command actions.",
        dest="command",
        metavar="",
    )

    create_parser = subparsers.add_parser(
        "create",
        help="Create a torrent file.",
        prefix_chars="-",
        aliases=["c"],
        formatter_class=HelpFormat,
    )

    create_parser.add_argument(
        "-p",
        "--private",
        action="store_true",
        dest="private",
        help="create file for private tracker",
    )

    create_parser.add_argument(
        "-s",
        "--source",
        action="store",
        dest="source",
        metavar="<source>",
        help="specify source tracker",
    )

    create_parser.add_argument(
        "-c",
        "--comment",
        action="store",
        dest="comment",
        metavar="<comment>",
        help="include a comment in file metadata",
    )

    create_parser.add_argument(
        "-o",
        "--out",
        action="store",
        dest="outfile",
        metavar="<path>",
        help="output path for created .torrent file",
    )

    create_parser.add_argument(
        "--meta-version",
        default="1",
        choices=["1", "2", "3"],
        action="store",
        dest="meta_version",
        metavar="<int>",
        help="""
        Bittorrent metafile version.
        Options = 1, 2 or 3.
        (1) = Bittorrent v1 (Default)
        (2) = Bittorrent v2
        (3) = Bittorrent v1 & v2 hybrid
        """,
    )

    create_parser.add_argument(
        "--piece-length",
        action="store",
        dest="piece_length",
        metavar="<int>",
        help="""
        Fixed amount of bytes for each chunk of data. (Default: None)
        Acceptable input values include integers 14-24, which
        will be interpreted as the exponent for 2^n, or any perfect
        power of two integer between 16Kib and 16MiB (inclusive).
        Examples:: [--piece-length 14] [-l 20] [-l 16777216]
        """,
    )

    create_parser.add_argument(
        "-t",
        "--tracker",
        action="store",
        dest="announce",
        metavar="<url>",
        nargs="+",
        default="",
        help="""
        One or more Bittorrent tracker announce url(s).
        Examples:: [-a url1 url2 url3]  [--anounce url1]
        """,
    )

    create_parser.add_argument(
        "-w",
        "--web-seed",
        action="store",
        dest="url_list",
        metavar="<url>",
        nargs="+",
        help="""
        One or more url(s) linking to a http server hosting
        the torrent contents.  This is useful if the torrent
        tracker is ever unreachable. Example:: [-w url1 [url2 [url3]]]
        """,
    )

    create_parser.add_argument(
        "content",
        action="store",
        metavar="<content>",
        help="path to content file or directory",
    )

    check_parser = subparsers.add_parser(
        "recheck",
        help="Recheck/Check torrent download completion",
        aliases=["r", "check"],
        prefix_chars="-",
        formatter_class=HelpFormat,
    )

    check_parser.add_argument(
        "metafile",
        action="store",
        metavar="<*.torrent>",
        help="path to .torrent file.",
    )

    check_parser.add_argument(
        "content",
        action="store",
        metavar="<content>",
        help="path to content file or directory",
    )

    edit_parser = subparsers.add_parser(
        "edit",
        help="Edit a torrent file.",
        aliases=["e"],
        prefix_chars="-",
        formatter_class=HelpFormat,
    )

    edit_parser.add_argument(
        "metafile",
        action="store",
        help="path to *.torrent file",
        metavar="<*.torrent>",
    )

    edit_parser.add_argument(
        "--tracker",
        action="store",
        dest="announce",
        metavar="<url>",
        nargs="+",
        help="""
        replace current list of tracker/announce urls with one or more space
        seperated Bittorrent tracker announce url(s).
        """,
    )

    edit_parser.add_argument(
        "--web-seed",
        action="store",
        dest="url_list",
        metavar="<url>",
        nargs="+",
        help="""
        replace current list of web-seed urls with one or more space seperated url(s)
        """,
    )

    edit_parser.add_argument(
        "--private",
        action="store_true",
        help="If currently private, will make it public, if public then private.",
        dest="private",
    )

    edit_parser.add_argument(
        "--comment",
        help="replaces any existing comment with <comment>",
        metavar="<comment>",
        dest="comment",
        action="store",
    )

    edit_parser.add_argument(
        "--source",
        action="store",
        dest="source",
        metavar="<source>",
        help="replaces current source with <source>",
    )

    flags = parser.parse_args(args)
    print(flags)
    if flags.debug:
        level = logging.DEBUG
    else:
        level = logging.WARNING
    tlogger = logging.getLogger("tlogger")
    tlogger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(prog)s %(asctime)s %(message)s",
            datefmt="%m-%d-%Y %H:%M:%S",
            style="%",
        )
    )
    tlogger.addHandler(handler)

    if flags.interactive:
        return select_action()

    if flags.command in ["recheck", "r", "check"]:
        tlogger.debug("Program entering Recheck mode.")
        metafile = flags.metafile
        content = flags.content
        tlogger.debug("Checking %s against %s contents", metafile, content)
        checker = Checker(metafile, content)
        tlogger.debug("Completed initialization of the Checker class")
        result = checker.results()
        tlogger.info("Final result for %s recheck:  %s", metafile, result)
        sys.stdout.write(str(result))
        sys.stdout.flush()
        return result

    if flags.command in ["edit", "e"]:
        metafile = flags.metafile
        editargs = {
            "url-list": flags.url_list,
            "announce": flags.announce,
            "source": flags.source,
            "private": flags.private,
            "comment": flags.comment,
        }
        return edit_torrent(metafile, editargs)

    kwargs = {
        "url_list": flags.url_list,
        "path": flags.content,
        "announce": flags.announce,
        "piece_length": flags.piece_length,
        "source": flags.source,
        "private": flags.private,
        "outfile": flags.outfile,
        "comment": flags.comment,
    }

    tlogger.debug("Program has entered torrent creation mode.")

    if flags.meta_version == "2":
        torrent = TorrentFileV2(**kwargs)
    elif flags.meta_version == "3":
        torrent = TorrentFileHybrid(**kwargs)
    else:
        torrent = TorrentFile(**kwargs)
    tlogger.debug("Completed torrent files meta info assembly.")
    outfile, meta = torrent.write()
    parser.kwargs = kwargs
    parser.meta = meta
    parser.outfile = outfile
    tlogger.debug("New torrent file (%s) has been created.", str(outfile))
    return parser


def main():
    """Initiate main function for CLI script."""
    main_script()
