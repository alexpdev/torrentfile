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
import os
import sys
from hashlib import sha1  # nosec
from urllib.parse import quote_plus

import pyben

from torrentfile.edit import edit_torrent
from torrentfile.interactive import select_action
from torrentfile.recheck import Checker
from torrentfile.torrent import TorrentFile, TorrentFileHybrid, TorrentFileV2

logger = logging.getLogger(__name__)


def create(args: list):
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
    kwargs = vars(args)
    logger.debug("Create new torrent file from %s", args.content)

    if args.meta_version == "2":
        torrent = TorrentFileV2(**kwargs)
    elif args.meta_version == "3":
        torrent = TorrentFileHybrid(**kwargs)
    else:
        torrent = TorrentFile(**kwargs)
    outfile, meta = torrent.write()
    print("Output path: ", str(outfile))
    logger.debug("Torrent file creation complete.")

    if args.magnet:
        magnet(outfile)

    args.torrent = torrent
    args.kwargs = kwargs
    args.outfile = outfile
    args.meta = meta

    logger.debug("New torrent file (%s) has been created.", str(outfile))
    return args


def info(args: list):
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
    if "private" in meta and meta["private"] == 1:
        meta["private"] = "True"
    if "announce-list" in meta:
        lst = meta["announce-list"]
        meta["announce-list"] = ", ".join([j for i in lst for j in i])
    if "url-list" in meta:
        meta["url-list"] = ", ".join(meta["url-list"])
    if "httpseeds" in meta:
        meta["httpseeds"] = ", ".join(meta["httpseeds"])
    text = []
    longest = max([len(i) for i in meta.keys()])
    for key, val in meta.items():
        if key not in ["pieces", "piece layers", "files", "file tree"]:
            prefix = longest - len(key) + 1
            string = key + (" " * prefix) + str(val)
            text.append(string)
    most = max([len(i) for i in text])
    text = ["-" * most, "\n"] + text + ["\n", "-" * most]
    output = "\n".join(text)
    print(output)
    return output


def edit(args: list):
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
        "httpseeds": args.httpseeds,
        "announce": args.announce,
        "source": args.source,
        "private": args.private,
        "comment": args.comment,
    }
    return edit_torrent(metafile, editargs)


def recheck(args):
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

    sys.stdout.write(str(result) + "% Match\n")
    sys.stdout.flush()
    return result


def magnet(metafile):
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
    sys.stdout.write("\n" + full_uri + "\n")
    return full_uri


interactive = select_action  # for clean import system
