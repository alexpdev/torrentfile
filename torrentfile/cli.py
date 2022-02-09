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

logger = logging.getLogger(__name__)


class TorrentFileHelpFormatter(HelpFormatter):
    """
    Formatting class for help tips provided by the CLI.

    Subclasses Argparse.HelpFormatter.
    """

    def __init__(self, prog, width=60, max_help_positions=40):
        """Construct HelpFormat class for usage output.

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
        """Split multiline help messages and remove indentation.

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
        """Format text for cli usage messages.

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
        """Combine different sections of the help message.

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
        """Format help message section headers.

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


def create_command(args):
    """Execute the create CLI sub-command to create a new torrent metafile.

    Parameters
    ----------
    args : argparse.Namespace
        positional and optional CLI arguments.

    Returns
    -------
    torrentfile.MetaFile
        object containing the path to created metafile and its contents.
    """
    kwargs = {
        "noprogress": args.noprogress,
        "url_list": args.url_list,
        "path": args.content,
        "announce": args.announce + args.tracker,
        "piece_length": args.piece_length,
        "source": args.source,
        "private": args.private,
        "outfile": args.outfile,
        "comment": args.comment,
    }

    logger.debug("Program has entered torrent creation mode.")

    if args.meta_version == "2":
        torrent = TorrentFileV2(**kwargs)
    elif args.meta_version == "3":
        torrent = TorrentFileHybrid(**kwargs)
    else:
        torrent = TorrentFile(**kwargs)
    logger.debug("Completed torrent files meta info assembly.")
    outfile, meta = torrent.write()

    if args.magnet:
        create_magnet(outfile)

    args.torrent = torrent
    args.kwargs = kwargs
    args.outfile = outfile
    args.meta = meta

    logger.debug("New torrent file (%s) has been created.", str(outfile))
    return args


def edit_command(args):
    """Execute the edit CLI sub-command with provided arguments.

    Parameters
    ----------
    args : Namespace
        positional and optional CLI arguments.

    Returns
    -------
    str
        path to edited torrent file.
    """
    metafile = args.metafile
    logger.info("Editing %s Meta File", str(args.metafile))
    editargs = {
        "url-list": args.url_list,
        "announce": args.announce,
        "source": args.source,
        "private": args.private,
        "comment": args.comment,
    }
    return edit_torrent(metafile, editargs)


def recheck_command(args):
    """Execute recheck CLI sub-command.

    Parameters
    ----------
    args : Namespace
        positional and optional arguments.

    Returns
    -------
    str
        The percentage of content currently saved to disk.
    """
    logger.debug("Program entering Recheck mode.")
    metafile = args.metafile
    content = args.content
    logger.debug("Checking %s against %s contents", metafile, content)
    checker = Checker(metafile, content)
    logger.debug("Completed initialization of the Checker class")
    result = checker.results()
    logger.info("Final result for %s recheck:  %s", metafile, result)
    sys.stdout.write(str(result))
    sys.stdout.flush()
    return result


def create_magnet(metafile):
    """Create a magnet URI from a Bittorrent meta file.

    Parameters
    ----------
    metafile : (Namespace||str)
        Namespace class for CLI arguments.

    Returns
    -------
    str
        created magnet URI.
    """
    import os
    from hashlib import sha1  # nosec
    from urllib.parse import quote_plus

    import pyben

    if hasattr(metafile, "metafile"):
        metafile = metafile.metafile
    if not os.path.exists(metafile):
        raise FileNotFoundError
    meta = pyben.load(metafile)
    info = meta["info"]
    binfo = pyben.dumps(info)
    infohash = sha1(binfo).hexdigest().upper()  # nosec
    logger.info("Magnet Info Hash: %s", infohash)
    scheme = "magnet:"
    hasharg = "?xt=urn:btih:" + infohash
    namearg = "&dn=" + quote_plus(info["name"])
    if "announce-list" in meta:
        announce_args = [
            "&tr=" + quote_plus(url)
            for urllist in meta["announce-list"]
            for url in urllist
        ]
    else:
        announce_args = ["&tr=" + quote_plus(meta["announce"])]
    full_uri = "".join([scheme, hasharg, namearg] + announce_args)
    logger.info("Created Magnet URI %s", full_uri)
    sys.stdout.write(full_uri)
    return full_uri


def main_script(args=None):
    """Initialize Command Line Interface for torrentfile.

    Parameters
    ----------
    args : list
        Commandline arguments. default=None
    """
    if not args:
        if sys.argv[1:]:
            args = sys.argv[1:]
        else:
            args = ["-h"]

    parser = ArgumentParser(
        "torrentfile",
        description="""
        CLI Tool for creating, checking, editing... Bittorrent meta files.
        TorrentFile supports all versions of torrent files.
        """,
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
        title="Actions",
        dest="command",
        metavar="<create> <edit> <magnet> <recheck>",
    )

    create_parser = subparsers.add_parser(
        "c",
        help="""
        Create a torrent meta file.
        """,
        prefix_chars="-",
        aliases=["create", "new"],
        formatter_class=TorrentFileHelpFormatter,
    )

    create_parser.add_argument(
        "-a",
        "--announce",
        action="store",
        dest="announce",
        metavar="<url>",
        nargs="+",
        default=[],
        help="Alias for -t/--tracker",
    )

    create_parser.add_argument(
        "-p",
        "--private",
        action="store_true",
        dest="private",
        help="Create a private torrent file",
    )

    create_parser.add_argument(
        "-s",
        "--source",
        action="store",
        dest="source",
        metavar="<source>",
        help="Useful for cross-seeding",
    )

    create_parser.add_argument(
        "-m",
        "--magnet",
        action="store_true",
        dest="magnet",
        help="Output Magnet Link after creation completes",
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
        help="Output path for created .torrent file",
    )

    create_parser.add_argument(
        "-t",
        "--tracker",
        action="store",
        dest="tracker",
        metavar="<url>",
        nargs="+",
        default=[],
        help="""One or more Bittorrent tracker announce url(s).""",
    )

    create_parser.add_argument(
        "--noprogress",
        action="store_true",
        dest="noprogress",
        help="""
        Disable showing the progress bar during torrent creation.
        (Minimially improves performance of torrent file creation.)
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
        Examples:: [--piece-length 14] [--piece-length 16777216]
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
        tracker is ever unreachable. Example:: -w url1 url2 url3
        """,
    )

    create_parser.add_argument(
        "content",
        action="store",
        metavar="<content>",
        help="Path to content file or directory",
    )

    create_parser.set_defaults(func=create_command)

    edit_parser = subparsers.add_parser(
        "e",
        help="""
        Edit existing torrent meta file.
        """,
        aliases=["edit"],
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
        help="""
        Replace current list of web-seed urls with one or more space seperated url(s)
        """,
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

    edit_parser.set_defaults(func=edit_command)

    magnet_parser = subparsers.add_parser(
        "m",
        help="""
        Create magnet url from an existing Bittorrent meta file.
        """,
        aliases=["magnet"],
        prefix_chars="-",
        formatter_class=TorrentFileHelpFormatter,
    )

    magnet_parser.add_argument(
        "metafile",
        action="store",
        help="Path to Bittorrent meta file.",
        metavar="<*.torrent>",
    )

    magnet_parser.set_defaults(func=create_magnet)

    check_parser = subparsers.add_parser(
        "r",
        help="""
        Calculate amount of torrent meta file's content is found on disk.
        """,
        aliases=["recheck", "check"],
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

    check_parser.set_defaults(func=recheck_command)
    args = parser.parse_args(args)

    if args.debug:
        torrentfile.add_handler()

    logger.debug(str(args))
    if args.interactive:
        return select_action()

    return args.func(args)


def main():
    """Initiate main function for CLI script."""
    main_script()
