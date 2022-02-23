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
The commands module contains the Action Commands executed by the CLI script.

Each function pertains to a command line action/subcommand and drives specific
features of the application.

Functions
---------
create_command
info_command
edit_command
recheck_command
magnet_command
"""
import logging
import sys

import pyben

from torrentfile.edit import edit_torrent
from torrentfile.recheck import Checker
from torrentfile.torrent import TorrentFile, TorrentFileHybrid, TorrentFileV2

logger = logging.getLogger(__name__)


def create_command(args):
    """
    Execute the create CLI sub-command to create a new torrent metafile.

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
        magnet_command(outfile)

    args.torrent = torrent
    args.kwargs = kwargs
    args.outfile = outfile
    args.meta = meta

    logger.debug("New torrent file (%s) has been created.", str(outfile))
    return args


def info_command(args):
    """
    Show torrent metafile details to user via stdout.

    Parameters
    ----------
    args : dict
        command line arguements provided by the user.
    """
    metafile = args.metafile
    meta = pyben.load(metafile)
    info = meta["info"]
    del meta["info"]
    meta.update(info)
    text = []
    longest = max([len(i) for i in meta.keys()])
    for key, val in meta.items():
        if key not in ["pieces", "piece layers"]:
            prefix = longest - len(key) + 1
            string = key + (" " * prefix) + str(val)
            text.append(string)
    output = "\n".join(text)
    print(output)
    return output


def edit_command(args):
    """
    Execute the edit CLI sub-command with provided arguments.

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
    """
    Execute recheck CLI sub-command.

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


def magnet_command(metafile):
    """
    Create a magnet URI from a Bittorrent meta file.

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
