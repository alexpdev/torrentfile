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
"""Edit torrent meta file."""

import os

import pyben


def filter_empty(args, meta, info):
    """
    Remove dictionary keys with empty values.

    Parameters
    ----------
    args : `dict`
        Editable metafile properties from user.
    meta : `dict`
        Metafile data dictionary.
    info : `dict`
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


def edit_torrent(metafile, args):
    """
    Edit the properties and values in a torrent meta file.

    Parameters
    ----------
    metafile : `str`
        path to the torrent meta file.
    args : `dict`
        key value pairs of the properties to be edited.
    """
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
            meta["announce list"] = [vallist]
        elif isinstance(val, list):
            meta["announce"] = val[0]
            meta["announce list"] = [val]

    if "url-list" in args:
        val = args.get("url-list")
        if isinstance(val, str):
            meta["url-list"] = val.split()
        elif isinstance(val, list):
            meta["url-list"] = val

    meta["info"] = info
    os.remove(metafile)
    pyben.dump(meta, metafile)
    return meta
