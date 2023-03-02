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
import logging
import sys
from argparse import ArgumentParser, HelpFormatter

from torrentfile.commands import (create, edit, info, magnet, rebuild, recheck,
                                  rename)
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

    def __init__(self, prog, width=45, max_help_positions=45):
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
            "Command line tools for creating, editing, checking, building "
            "and interacting with Bittorrent metainfo files"
        ),
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
        "-f",
        "--config",
        action="store_true",
        dest="config",
        help="""
        Parse torrent information from a config file. Looks in the current
        working directory, or the directory named .torrentfile in the users
        home directory for a torrentfile.ini file. You can also use this
        option in combination with the --config-path to specify the path to
        the config file. See documentation for details on properly formatting
        config file.
        """,
    )

    create_parser.add_argument(
        "--config-path",
        action="store",
        metavar="<path>",
        dest="config_path",
        help="""
        Use this option in combination with -f or --config
        options to specify location of config file.
        """,
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
        help="Explicitly specify the path to write the file.",
    )

    create_parser.add_argument(
        "--cwd",
        "--current",
        action="store_true",
        dest="cwd",
        help="*deprecated* Saving to current directory is default behaviour",
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
        (1) = Display progress bar.(default)
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
        (Default: auto calculated based on total size of content) Number of
        bytes for per chunk of data transmitted by Bittorrent client.
        Acceptable values include integers 14-26 which will be interpreted
        as exponent for power of 2.  e.g. 14 = 16KiB pieces.
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
        help="""Edit existing torrent meta file.""",
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

    info_parser = subparsers.add_parser(
        "info",
        help="Show detailed information about a torrent file.",
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

    magnet_parser = subparsers.add_parser(
        "magnet",
        help="Generate magnet url from an existing Bittorrent meta file.",
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
        help="Gives a detailed look at how much of the torrent is available.",
        aliases=["check", "r"],
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

    rebuild_parser = subparsers.add_parser(
        "rebuild",
        help="""Re-assemble files obtained from a bittorrent file into the
                appropriate file structure for re-seeding.  Read documentation
                for more information, or use cases.""",
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
        "-c" "--contents",
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

    rebuild_parser.set_defaults(func=rebuild)

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
        help="path to file that needs renaming.",
    )

    rename_parser.set_defaults(func=rename)

    all_commands = [
        "create",
        "new",
        "c",
        "edit",
        "e",
        "info",
        "i",
        "magnet",
        "m",
        "recheck",
        "check",
        "r",
        "rename",
        "rebuild",
        "-i",
        "-h",
        "-V",
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


def main():
    """
    Initiate main function for CLI script.
    """
    execute()
