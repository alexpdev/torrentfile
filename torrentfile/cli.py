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

    def __init__(self, prog: str, width=75, max_help_pos=60):
        """Construct HelpFormat class."""
        super().__init__(prog, width=width, max_help_position=max_help_pos)

    def _split_lines(self, text, _):
        """Split multiline help messages and remove indentation."""
        lines = text.split("\n")
        return [line.strip() for line in lines if line]

    def _format_text(self, text):
        text = text % dict(prog=self._prog) if '%(prog)' in text else text
        text = self._whitespace_matcher.sub(' ', text).strip()
        return text + "\n\n"


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
        title="Actions",
        description="Each sub-command triggers a specific action.",
        dest="command",
    )

    create_parser = subparsers.add_parser(
        "c",
        help="""
        Create a torrent meta file.
        """,
        prefix_chars="-",
        aliases=["create", "new"],
        formatter_class=HelpFormat,
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
        help="Create a private torrent meta file",
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
        "-m",
        "--magnet",
        action="store_true",
        dest="magnet",
        help="output Magnet Link after creation completes",
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
        "--progress",
        action="store_true",
        dest="progress",
        help="""
        Enable showing the progress bar during torrent creation.
        (Minimially impacts the duration of torrent file creation.)
        """
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
        metavar="<content path>",
        help="path to content file or directory",
    )

    edit_parser = subparsers.add_parser(
        "e",
        help="""
        Edit existing torrent meta file.
        """,
        aliases=["edit"],
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

    magnet_parser = subparsers.add_parser(
        "m",
        help="""
        Create magnet url from an existing Bittorrent meta file.
        """,
        aliases=["magnet"],
        prefix_chars="-",
        formatter_class=HelpFormat,
    )

    magnet_parser.add_argument(
        "metafile",
        action="store",
        help="path to Bittorrent meta file.",
        metavar="<*.torrent>",
    )

    check_parser = subparsers.add_parser(
        "r",
        help="""
        Calculate amount of torrent meta file's content is found on disk.
        """,
        aliases=["recheck", "check"],
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

    flags = parser.parse_args(args)

    if flags.debug:
        torrentfile.setLevel(logging.DEBUG)

    logger.debug(str(flags))
    if flags.interactive:
        return select_action()

    if flags.command in ["m", "magnet"]:
        return create_magnet(flags.metafile)

    if flags.command in ["recheck", "r", "check"]:
        logger.debug("Program entering Recheck mode.")
        metafile = flags.metafile
        content = flags.content
        logger.debug("Checking %s against %s contents", metafile, content)
        checker = Checker(metafile, content)
        logger.debug("Completed initialization of the Checker class")
        result = checker.results()
        logger.info("Final result for %s recheck:  %s", metafile, result)
        sys.stdout.write(str(result))
        sys.stdout.flush()
        return result

    if flags.command in ["edit", "e"]:
        metafile = flags.metafile
        logger.info("Editing %s" % flags.metafile)
        editargs = {
            "url-list": flags.url_list,
            "announce": flags.announce,
            "source": flags.source,
            "private": flags.private,
            "comment": flags.comment,
        }
        return edit_torrent(metafile, editargs)

    kwargs = {
        "progress": flags.progress,
        "url_list": flags.url_list,
        "path": flags.content,
        "announce": flags.announce + flags.tracker,
        "piece_length": flags.piece_length,
        "source": flags.source,
        "private": flags.private,
        "outfile": flags.outfile,
        "comment": flags.comment,
    }

    logger.debug("Program has entered torrent creation mode.")

    if flags.meta_version == "2":
        torrent = TorrentFileV2(**kwargs)
    elif flags.meta_version == "3":
        torrent = TorrentFileHybrid(**kwargs)
    else:
        torrent = TorrentFile(**kwargs)
    logger.debug("Completed torrent files meta info assembly.")
    outfile, meta = torrent.write()
    if flags.magnet:
        create_magnet(outfile)
    parser.kwargs = kwargs
    parser.meta = meta
    parser.outfile = outfile
    logger.debug("New torrent file (%s) has been created.", str(outfile))
    return parser


def main():
    """Initiate main function for CLI script."""
    main_script()


def create_magnet(metafile):
    """Create a magnet URI from a Bittorrent meta file.

    Parameters
    ----------
    metafile : `str` | `os.PathLike`
        path to bittorrent meta file.

    Returns
    -------
    `str`
        created magnet URI.
    """
    import os
    from hashlib import sha1  # nosec
    from urllib.parse import quote_plus

    import pyben

    if not os.path.exists(metafile):
        raise FileNotFoundError
    meta = pyben.load(metafile)
    info = meta["info"]
    binfo = pyben.dumps(info)
    infohash = sha1(binfo).hexdigest().upper()  # nosec
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
    sys.stdout.write(full_uri)
    return full_uri
