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
Edit torrent module.

Provides a facility by which certain properties of a torrent meta file can be
edited by the user. The various command line arguments indicate which fields
should be edited, and what the new value should be.  Depending on what fields
are chosen to edit, this command can trigger a new info hash which means the
torrent will no longer be able to participate in the same swarm as the original
unedited torrent.

Keywords
--------
private
comment
source
trackers
web-seeds
"""

import logging
import os

import pyben

logger = logging.getLogger(__name__)


def filter_empty(args: dict, meta: dict, info: dict):
    """
    Remove the fields that were not used by the original file creator.

    Parameters
    ----------
    args : dict
        Editable metafile properties from user.
    meta : dict
        Metafile data dictionary.
    info : dict
        Metafile info dictionary.
    """
    for key, val in list(args.items()):
        if val is None:
            del args[key]
            continue

        if val == "":
            if key in meta:
                del meta[key]
            elif key in info:
                del info[key]
            del args[key]
            logger.debug("removeing empty fields %s", val)


def edit_torrent(metafile: str, args: dict) -> dict:
    """
    Edit the properties and values in a torrent meta file.

    Parameters
    ----------
    metafile : str
        path to the torrent meta file.
    args : dict
        key value pairs of the properties to be edited.

    Returns
    -------
    dict
        The edited and nested Meta and info dictionaries.
    """
    logger.debug("editing torrent file %s", metafile)
    meta = pyben.load(metafile)
    info = meta["info"]
    filter_empty(args, meta, info)

    if "comment" in args:
        info["comment"] = args["comment"]

    if "source" in args:
        info["source"] = args["source"]

    if "private" in args:
        info["private"] = 1

    if "announce" in args:
        val = args.get("announce", None)
        if isinstance(val, str):
            vallist = val.split()
            meta["announce"] = vallist[0]
            meta["announce-list"] = [vallist]
        elif isinstance(val, list):
            meta["announce"] = val[0]
            meta["announce-list"] = [val]

    if "url-list" in args:
        val = args.get("url-list")
        if isinstance(val, str):
            meta["url-list"] = val.split()
        elif isinstance(val, list):
            meta["url-list"] = val

    if "httpseeds" in args:
        val = args.get("httpseeds")
        if isinstance(val, str):
            meta["httpseeds"] = val.split()
        elif isinstance(val, list):
            meta["httpseeds"] = val

    meta["info"] = info
    os.remove(metafile)
    pyben.dump(meta, metafile)
    return meta
