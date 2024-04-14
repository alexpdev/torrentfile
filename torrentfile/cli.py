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

Functions
---------
main_script :
    process command line arguments and run program.
activate_logger :
    turns on debug mode and logging facility.

Classes
-------
Config : class
    controls logging configuration
TorrentFileHelpFormatter : HelpFormatter
    the command line help message formatter
"""

import io
import sys
import logging
from argparse import ArgumentParser, HelpFormatter

from torrentfile import commands
from torrentfile.utils import toggle_debug_mode
from torrentfile.version import __version__ as version


class Config:
    """
    Class the controls the logging configuration and output settings.

    Controls the logging level, or whether to app should operate in quiet mode.
    """

    @staticmethod
    def activate_quiet():
        """
        Activate quiet mode for the duration of the programs life.

        When quiet mode is enabled, no logging, progress or state information
        is output to the terminal
        """
        if sys.stdout or sys.stderr:
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()

    @staticmethod
    def activate_logger():
        """
        Activate the builtin logging mechanism when passed debug flag from CLI.
        """
        logging.basicConfig(level=logging.WARNING)
        logger = logging.getLogger()
        console_handler = logging.StreamHandler(stream=sys.stderr)
        stream_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelno)s] %(message)s",
            datefmt="%H:%M:%S",
            style="%",
        )
        console_handler.setFormatter(stream_formatter)
        console_handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(console_handler)
        logger.debug("Debug: ON")
        toggle_debug_mode(True)


class TorrentFileHelpFormatter(HelpFormatter):
    """
    Formatting class for help tips provided by the CLI.

    Subclasses Argparse.HelpFormatter.
    """

    def __init__(self,
                 prog: str,
                 width: int = 45,
                 max_help_positions: int = 45):
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
        super().__init__(prog,
                         width=width,
                         max_help_position=max_help_positions)

    def _split_lines(self, text: str, _: int) -> list:
        """
        Split multiline help messages and remove indentation.

        Parameters
        ----------
        text : str
            text that needs to be split
        _ : int
            max width for line.

        Returns
        -------
        list :
            split into multiline text list
        """
        lines = text.split("\n")
        return [line.strip() for line in lines if line]

    def _format_text(self, text: str) -> str:
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
        text = text % {"prog": self._prog} if "%(prog)" in text else text
        text = self._whitespace_matcher.sub(" ", text).strip()
        return text + "\n\n"

    def _join_parts(self, part_strings: list) -> str:
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
        parts = self._format_headers(part_strings)
        return super()._join_parts(parts)

    @staticmethod
    def _format_headers(parts: list) -> list:
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


def execute(args: list = None) -> list:
    """
    Execute program with provided list of arguments.

    If no arguments are given then it defaults to using
    sys.argv.  This is the main entrypoint for the program
    and command line interface.

    Parameters
    ----------
    args : list
        Commandline arguments. default=None

    Returns
    -------
    list
        Depends on what the command line args were.
    """
    toggle_debug_mode(False)
    if not args:
        if sys.argv[1:]:
            args = sys.argv[1:]
        else:
            args = ["-h"]

    parser = ArgumentParser(
        "torrentfile",
        usage="torrentfile <options>",
        description=(
            "Command line tool for creating, editing, validating, building "
            "and interacting with all versions of Bittorrent files"),
        prefix_chars="-",
        formatter_class=TorrentFileHelpFormatter,
        conflict_handler="resolve",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        help="Turn off all text output.",
        dest="quiet",
        action="store_true",
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
        title="Commands",
        dest="command",
        metavar="create, edit, info, magnet, recheck, rebuild, rename\n",
    )

    create_parser = subparsers.add_parser(
        "create",
        help="Create a new Bittorrent file.",
        prefix_chars="-",
        aliases=["new"],
        formatter_class=TorrentFileHelpFormatter,
    )

    create_parser.add_argument(
        "-a",
        "--announce",
        "--tracker",
        action="store",
        dest="announce",
        metavar="<url>",
        nargs="+",
        default=[],
        help="one or more space-seperated tracker url(s)",
    )

    create_parser.add_argument(
        "-p",
        "--private",
        action="store_true",
        dest="private",
        help="create private torrent",
    )

    create_parser.add_argument(
        "-s",
        "--source",
        action="store",
        dest="source",
        metavar="<source>",
        help="add source field to the metadata",
    )

    create_parser.add_argument(
        "--config",
        action="store_true",
        dest="config",
        help="""
        Parse torrent information from a config file. Looks in the current
        working directory, or the directory named .torrentfile in the users
        home directory for a torrentfile.ini file. See --config-path option.
        """,
    )

    create_parser.add_argument(
        "--config-path",
        action="store",
        metavar="<path>",
        dest="config_path",
        help="use in combination with --config to provide config file path",
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
        help="include a comment in the torrent file metadata",
    )

    create_parser.add_argument(
        "-o",
        "--out",
        action="store",
        dest="outfile",
        metavar="<path>",
        help="path to write torrent file",
    )


    create_parser.add_argument(
        "--ow",
        "--overwrite",
        action="store_true",
        dest="overwrite",
        help="overwrite output file if it already exists",
    )

    create_parser.add_argument(
        "--prog",
        "--progress",
        default="1",
        action="store",
        dest="progress",
        metavar="<int>",
        help="""
        set the progress bar level
        Options = 0, 1, 2
        (0) = Do not display progress bar.
        (1) = Display progress bar for each file.(default)
        (2) = Display one progress bar for full torrent.
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
        bittorrent metafile version
        options = 1, 2, 3
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
        (Default: auto calculated based on total size of content)
        acceptable values include numbers 14-26
        14 = 16KiB, 20 = 1MiB, 21 = 2MiB etc.  Examples:[--piece-length 14]
        """,
    )

    create_parser.add_argument(
        "--web-seed",
        action="store",
        dest="url_list",
        metavar="<url>",
        nargs="+",
        help="list of web addresses where torrent data exists (GetRight)",
    )

    create_parser.add_argument(
        "--http-seed",
        action="store",
        dest="httpseeds",
        metavar="<url>",
        nargs="+",
        help="list of URLs, addresses where content can be found (Hoffman)",
    )

    create_parser.add_argument(
        "--align",
        action="store_true",
        help=("Align pieces to file boundaries. "
              "This option is ignored when not used with V1 torrents."),
    )

    create_parser.add_argument(
        "content",
        action="store",
        metavar="<content>",
        nargs="?",
        help="path to content file or directory",
    )

    create_parser.set_defaults(func=commands.create)

    edit_parser = subparsers.add_parser(
        "edit",
        help="edit torrent file",
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
        help="replace current trackers with one or more urls",
    )

    edit_parser.add_argument(
        "--web-seed",
        action="store",
        dest="url_list",
        metavar="<url>",
        nargs="+",
        help="replace current web-seed with one or more url(s)",
    )

    edit_parser.add_argument(
        "--http-seed",
        action="store",
        dest="httpseeds",
        metavar="<url>",
        nargs="+",
        help="replace current http-seed urls with new ones (Hoffman)",
    )

    edit_parser.add_argument(
        "--private",
        action="store_true",
        help="make torrent private",
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

    edit_parser.set_defaults(func=commands.edit)

    info_parser = subparsers.add_parser(
        "info",
        help="show detailed information about a torrent file",
        prefix_chars="-",
        formatter_class=TorrentFileHelpFormatter,
    )

    info_parser.add_argument(
        "metafile",
        action="store",
        metavar="<*.torrent>",
        help="path to torrent file",
    )

    info_parser.set_defaults(func=commands.info)

    magnet_parser = subparsers.add_parser(
        "magnet",
        help="generate magnet url from an existing torrent file",
        aliases=["m"],
        prefix_chars="-",
        formatter_class=TorrentFileHelpFormatter,
    )

    magnet_parser.add_argument(
        "metafile",
        action="store",
        help="path to torrent file",
        metavar="<*.torrent>",
    )

    magnet_parser.add_argument(
        "--meta-version",
        action="store",
        choices=["0", "1", "2", "3"],
        default="0",
        help="""
        This option is only relevant for hybrid torrent files.
        Options = 0, 1, 2, 3
        (0) = [default] version is determined automatically
        (1) = create V1 magnet link only
        (2) = create V2 magnet link only
        (3) = create a hybrid magnet link
        """,
        dest="meta_version",
        metavar="<int>",
    )

    magnet_parser.set_defaults(func=commands.get_magnet)

    check_parser = subparsers.add_parser(
        "recheck",
        help="gives a detailed look at how much of the torrent is available",
        aliases=["check"],
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

    check_parser.set_defaults(func=commands.recheck)

    rebuild_parser = subparsers.add_parser(
        "rebuild",
        help="""
        Re-assemble files obtained from a bittorrent file into the
        appropriate file structure for re-seeding.  Read documentation
        for more information, or use cases.
        """,
        formatter_class=TorrentFileHelpFormatter,
    )

    rebuild_parser.add_argument(
        "-m",
        "--metafiles",
        action="store",
        metavar="<*.torrent>",
        nargs="+",
        dest="metafiles",
        required=True,
        help="path(s) to .torrent file(s)/folder(s) containing .torrent files",
    )

    rebuild_parser.add_argument(
        "-c"
        "--contents",
        action="store",
        dest="contents",
        nargs="+",
        required=True,
        metavar="<contents>",
        help="folders that might contain the source contents needed to rebuld",
    )

    rebuild_parser.add_argument(
        "-d",
        "--destination",
        action="store",
        dest="destination",
        required=True,
        metavar="<destination>",
        help="path to where torrents will be re-assembled",
    )

    rebuild_parser.set_defaults(func=commands.rebuild)

    rename_parser = subparsers.add_parser(
        "rename",
        help="""Rename a torrent file to it's original name provided in the
                metadata/the same name you see in your torrent client.""",
        formatter_class=TorrentFileHelpFormatter,
    )

    rename_parser.add_argument(
        "target",
        action="store",
        metavar="<target>",
        help="path to torrent file",
    )

    rename_parser.set_defaults(func=commands.rename)

    all_commands = [
        "m",
        "-h",
        "-V",
        "new",
        "edit",
        "info",
        "check",
        "create",
        "magnet",
        "rename",
        "rebuild",
        "recheck",
    ]
    if not any(i for i in all_commands if i in args):
        start = 0
        while args[start] in ["-v", "-q"]:
            start += 1
        args.insert(start, "create")

    args = parser.parse_args(args)

    if args.quiet:
        Config.activate_quiet()

    elif args.debug:
        Config.activate_logger()

    if hasattr(args, "func"):
        return args.func(args)
    return args  # pragma: nocover


main_script = execute


def main() -> None:
    """
    Initiate main function for CLI script.
    """
    execute()
