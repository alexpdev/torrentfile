#! /usr/bin/python3
# -*- coding: utf-8 -*-

##############################################################################
#    Copyright (C) 2021-current alexpdev
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
##############################################################################
"""
Command Line Interface for TorrentFile project.

This module provides the primary command line argument parser for
the torrentfile package. The main_script function is automatically
invoked when called from command line, and parses accompanying arguments.

Functions:
    main_script: process command line arguments and run program.
    activate_logger: turns on debug mode and logging facility.
"""

import logging
import sys
from argparse import ArgumentParser, HelpFormatter

from torrentfile.commands import create, edit, info, magnet, recheck
from torrentfile.interactive import select_action
from torrentfile.version import __version__ as version


def activate_logger():
    """
    Activate the builtin logging mechanism when passed debug flag from CLI.
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    # file_handler = logging.FileHandler(
    #     "torrentfile.log", mode="a+", encoding="utf-8"
    # )
    console_handler = logging.StreamHandler(stream=sys.stderr)
    # file_formatter = logging.Formatter(
    #     "%(asctime)s %(levelno)s %(message)s",
    #     datefmt="%m-%d %H:%M:%S",
    #     style="%",
    # )
    stream_formatter = logging.Formatter(
        "%(asctime)s %(levelno)s %(message)s",
        datefmt="%m-%d %H:%M:%S",
        style="%",
    )
    # file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(stream_formatter)
    # file_handler.setLevel(logging.INFO)
    console_handler.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    # logger.addHandler(file_handler)
    logger.debug("Debug: ON")


class TorrentFileHelpFormatter(HelpFormatter):
    """
    Formatting class for help tips provided by the CLI.

    Subclasses Argparse.HelpFormatter.
    """

    def __init__(self, prog, width=40, max_help_positions=30):
        """
        Construct HelpFormat class for usage output.

        Parameters
        ----------
        prog : str
            Name of the program.
        width : int
            Max width of help message output.
        max_help_positions : int
            max length until line wrap.
        """
        super().__init__(
            prog, width=width, max_help_position=max_help_positions
        )

    def _split_lines(self, text, _):
        """
        Split multiline help messages and remove indentation.

        Parameters
        ----------
        text : str
            text that needs to be split
        _ : int
            max width for line.
        """
        lines = text.split("\n")
        return [line.strip() for line in lines if line]

    def _format_text(self, text):
        """
        Format text for cli usage messages.

        Parameters
        ----------
        text : str
            Pre-formatted text.

        Returns
        -------
        str
            Formatted text from input.
        """
        text = text % dict(prog=self._prog) if "%(prog)" in text else text
        text = self._whitespace_matcher.sub(" ", text).strip()
        return text + "\n\n"

    def _join_parts(self, part_strings):
        """
        Combine different sections of the help message.

        Parameters
        ----------
        part_strings : list
            List of argument help messages and headers.

        Returns
        -------
        str
            Fully formatted help message for CLI.
        """
        parts = self.format_headers(part_strings)
        return super()._join_parts(parts)

    @staticmethod
    def format_headers(parts):
        """
        Format help message section headers.

        Parameters
        ----------
        parts : list
            List of individual lines for help message.

        Returns
        -------
        list
            Input list with formatted section headers.
        """
        if parts and parts[0].startswith("usage:"):
            parts[0] = "Usage\n=====\n  " + parts[0][6:]
        headings = [i for i in range(len(parts)) if parts[i].endswith(":\n")]
        for i in headings[::-1]:
            parts[i] = parts[i][:-2].title()
            underline = "".join(["\n", "-" * len(parts[i]), "\n"])
            parts.insert(i + 1, underline)
        return parts


def execute(args=None) -> list:
    """
    Initialize Command Line Interface for torrentfile.

    Parameters
    ----------
    args : list
        Commandline arguments. default=None

    Returns
    -------
    list
        Depends on what the command line args were.
    """
    if not args:
        if sys.argv[1:]:
            args = sys.argv[1:]
        else:
            args = ["-h"]

    parser = ArgumentParser(
        "torrentfile",
        description=(
            "Command line tools for creating, editing, checking and "
            "interacting with Bittorrent metainfo files"
        ),
        prefix_chars="-",
        formatter_class=TorrentFileHelpFormatter,
        conflict_handler="resolve",
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
        version=f"torrentfile v{version}",
        help="show program version and exit",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="debug",
        help="output debug information",
    )

    parser.set_defaults(func=parser.print_help)

    subparsers = parser.add_subparsers(
        title="Actions",
        dest="command",
        metavar="create, edit, magnet, recheck",
    )

    create_parser = subparsers.add_parser(
        "create",
        help="""Generate a new torrent meta file.""",
        prefix_chars="-",
        aliases=["c", "new"],
        formatter_class=TorrentFileHelpFormatter,
    )

    create_parser.add_argument(
        "-a",
        "-t",
        "--announce",
        "--tracker",
        action="store",
        dest="announce",
        metavar="<url>",
        nargs="+",
        default=[],
        help="One or more space-seperated torrent tracker url(s).",
    )

    create_parser.add_argument(
        "-p",
        "--private",
        action="store_true",
        dest="private",
        help="Creates private torrent with multi-tracker and DHT turned off.",
    )

    create_parser.add_argument(
        "-s",
        "--source",
        action="store",
        dest="source",
        metavar="<source>",
        help="Add a source string. Useful for cross-seeding.",
    )

    create_parser.add_argument(
        "-m",
        "--magnet",
        action="store_true",
        dest="magnet",
    )

    create_parser.add_argument(
        "-c",
        "--comment",
        action="store",
        dest="comment",
        metavar="<comment>",
        help="Include a comment in file metadata",
    )

    create_parser.add_argument(
        "-o",
        "--out",
        action="store",
        dest="outfile",
        metavar="<path>",
        help="Output save path for created .torrent file",
    )

    create_parser.add_argument(
        "--cwd",
        "--current",
        action="store_true",
        dest="cwd",
        help="Save output .torrent file to current directory",
    )

    create_parser.add_argument(
        "--prog",
        "--progress",
        default="1",
        action="store",
        dest="progress",
        help="""
        Set the progress bar level.
        Options = 0, 1
        (0) = Do not display progress bar.
        (1) = Display progress bar.
        """,
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
        Options = 1, 2, 3
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
        (Default: <blank>) Number of bytes for per chunk of data transmitted
        by Bittorrent client. Acceptable values include integers 14-26 which
        will be interpreted as a perfect power of 2.  e.g. 14 = 16KiB pieces.
        Examples:: [--piece-length 14] [--piece-length 20]
        """,
    )

    create_parser.add_argument(
        "-w",
        "--web-seed",
        action="store",
        dest="url_list",
        metavar="<url>",
        nargs="+",
        help="list of web addresses where torrent data exists (GetRight).",
    )

    create_parser.add_argument(
        "--http-seed",
        action="store",
        dest="httpseeds",
        metavar="<url>",
        nargs="+",
        help="list of URLs, addresses where content can be found (Hoffman).",
    )

    create_parser.add_argument(
        "content",
        action="store",
        metavar="<content>",
        nargs="?",
        help="Path to content file or directory",
    )

    create_parser.set_defaults(func=create)

    edit_parser = subparsers.add_parser(
        "edit",
        help="""
        Edit existing torrent meta file.
        """,
        aliases=["e"],
        prefix_chars="-",
        formatter_class=TorrentFileHelpFormatter,
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
        Replace current list of tracker/announce urls with one or more space
        seperated Bittorrent tracker announce url(s).
        """,
    )

    edit_parser.add_argument(
        "--web-seed",
        action="store",
        dest="url_list",
        metavar="<url>",
        nargs="+",
        help="Replace current list of web-seed urls with one or more url(s)",
    )

    edit_parser.add_argument(
        "--http-seed",
        action="store",
        dest="httpseeds",
        metavar="<url>",
        nargs="+",
        help="replace all currently listed addresses with new list (Hoffman).",
    )

    edit_parser.add_argument(
        "--private",
        action="store_true",
        help="Make torrent private.",
        dest="private",
    )

    edit_parser.add_argument(
        "--comment",
        help="Replaces any existing comment with <comment>",
        metavar="<comment>",
        dest="comment",
        action="store",
    )

    edit_parser.add_argument(
        "--source",
        action="store",
        dest="source",
        metavar="<source>",
        help="Replaces current source with <source>",
    )

    edit_parser.set_defaults(func=edit)

    magnet_parser = subparsers.add_parser(
        "magnet",
        help="""
        Generate magnet url from an existing Bittorrent meta file.
        """,
        aliases=["m"],
        prefix_chars="-",
        formatter_class=TorrentFileHelpFormatter,
    )

    magnet_parser.add_argument(
        "metafile",
        action="store",
        help="Path to Bittorrent meta file.",
        metavar="<*.torrent>",
    )

    magnet_parser.set_defaults(func=magnet)

    check_parser = subparsers.add_parser(
        "recheck",
        help="""
        Calculate amount of torrent meta file's content is found on disk.
        """,
        aliases=["r", "check"],
        prefix_chars="-",
        formatter_class=TorrentFileHelpFormatter,
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

    check_parser.set_defaults(func=recheck)

    info_parser = subparsers.add_parser(
        "info",
        help="""
        Show detailed information about a torrent file.
        """,
        aliases=["i"],
        prefix_chars="-",
        formatter_class=TorrentFileHelpFormatter,
    )

    info_parser.add_argument(
        "metafile",
        action="store",
        metavar="<*.torrent>",
        help="path to pre-existing torrent file.",
    )

    info_parser.set_defaults(func=info)

    args = parser.parse_args(args)

    if args.debug:
        activate_logger()

    if args.interactive:
        return select_action()

    if hasattr(args, "func"):
        return args.func(args)
    return args


main_script = execute


def main():
    """
    Initiate main function for CLI script.
    """
    execute()
