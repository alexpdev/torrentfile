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
Clases and functions for the rebuild or reassemble subcommand.

Re-assemble a torrent into the propper directory structure as indicated by a
torrent meta file, and validate the contents of each file allong the
way. Displays a progress bar for each torrent.
"""
import os
from copy import deepcopy
from hashlib import sha1
from pathlib import Path

import pyben

from torrentfile.hasher import HasherV2
from torrentfile.utils import copypath


class Metadata:
    """
    Class containing the metadata contents of a torrent file.
    """

    def __init__(self, path: str):
        """
        Construct metadata object for torrent info.

        Parameters
        ----------
        path : str
            path to the .torrent file.
        """
        self.path = os.path.abspath(path)
        self.meta = None
        self.name = None
        self.info = None
        self.length = 0
        self.files = []
        self.filenames = set()
        self.extract()

    def extract(self):
        """
        Decode and extract information for the .torrent file.
        """
        self.meta = pyben.load(self.path)
        info = self.meta["info"]
        self.piece_length = info["piece length"]
        self.name = info["name"]
        self.meta_version = info.get("meta version", 1)
        self.pieces = info.get("pieces", bytes())
        if self.meta_version == 2:
            self._parse_tree(info["file tree"], [self.name])
        elif "length" in info:
            self.length += info["length"]
            self.is_file = True
            self.filenames.add(info["name"])
            self.files.append(
                {
                    "path": Path(self.name).parent,
                    "filename": self.name,
                    "full": self.name,
                    "length": self.length,
                }
            )
        elif "files" in info:
            for f in info["files"]:
                path = f["path"]
                full = os.path.join(self.name, *path)
                self.files.append(
                    {
                        "path": Path(full).parent,
                        "filename": path[-1],
                        "full": full,
                        "length": f["length"],
                    }
                )
                self.length += f["length"]
                self.filenames.add(path[-1])

    def _parse_tree(self, tree: dict, partials: list):
        """
        Parse the file tree dictionary of the torrent metafile.

        Parameters
        ----------
        tree : dict
            the dictionary representation of a file tree.
        partials : list
            list of paths leading up to the current key value.
        """
        for key, val in tree.items():
            if "" in val:
                self.filenames.add(key)
                path = Path(os.path.join(*partials))
                full = Path(os.path.join(path, key))
                length = val[""]["length"]
                root = val[""]["pieces root"]
                self.files.append(
                    {
                        "path": path,
                        "full": full,
                        "filename": key,
                        "length": length,
                        "root": root,
                    }
                )
                self.length += length
            else:
                self._parse_tree(val, partials + [key])


class Assembler:
    """
    Does most of the work in attempting the structure of torrentfiles.

    Requires three paths as arguments.
    - torrent metafile or directory containing multiple meta files
    - directory containing the contents of meta file
    - directory where torrents will be re-assembled
    """

    def __init__(self, metafiles: list, contents: list, dest: str):
        """
        Construct the assembler object.

        Takes two paths as parameters,
        - file or directory containing 1 or more torrent meta files
        - path to where the contents are belived to be located.

        Parameters
        ----------
        metafiles : str
            path to torrent metafile or directory containing torrent metafiles.
        contents : str
            path to content or directory containing content that belongs to
            torrentfile.
        dest: str
            path to the directory where rebuild will take place.
        """
        self.contents = contents
        self.filemap = _index_contents(self.contents)
        self.metafiles = _get_metafiles(metafiles)
        self.dest = dest
        self.counter = 0

    def assemble_torrents(self) -> int:
        """
        Assemble collection of torrent files into original structure.

        Returns
        -------
        int
            number of files copied
        """
        for metafile in self.metafiles:
            self.rebuild(metafile)
        return self.counter

    def _rebuild_v2(self, metafile: Metadata) -> None:
        """
        Rebuild method for torrent v2 files.

        Parameters
        ----------
        metafile : Metadata
            the metafile object
        """
        for entry in metafile.files:
            filename = entry["filename"]
            length = entry["length"]
            if filename in self.filemap:
                paths = self.filemap[filename]
            else:
                continue  # pragma: nocover
            for path, size in paths:
                if size == length:
                    hasher = HasherV2(path, metafile.piece_length, True)
                    if entry["root"] == hasher.root:
                        dest_path = os.path.join(self.dest, entry["full"])
                        copypath(entry["path"], dest_path)
                        self.counter += 1
                        break
                if self.counter and self.counter % 20 == 0:
                    print(
                        f"Success {self.counter}: {entry['path']} -> {path}"
                    )  # pragma: nocover

    def rebuild(self, metafile: Metadata) -> None:
        """
        Build the torrent file structure from contents of directory.

        Traverse contents dir and compare discovered files
        with files listed in torrent metadata and copy
        the matches to the destination directory respecting folder
        structures along the way.
        """
        if metafile.meta_version == 2:
            self._rebuild_v2(metafile)
        else:
            self._rebuild_v1(metafile)

    def _rebuild_v1(self, metafile: Metadata) -> None:
        """
        Rebuild method for torrent v1 files.

        Parameters
        ----------
        metafile : Metadata
            metafile object
        """
        partial = bytes()
        for val in metafile.files:
            found = False
            if val["filename"] in self.filemap:
                for path, size in self.filemap[val["filename"]]:
                    if size == val["length"]:
                        pieces = deepcopy(metafile.pieces)
                        pl = metafile.piece_length
                        result = self.check_hashes(path, pieces, partial, pl)
                        if len(result) == 0:
                            continue
                        partial, metafile.pieces = result[0], result[1]
                        dest_path = os.path.join(self.dest, val["full"])
                        found = True
                        copypath(path, dest_path)
                        self.counter += 1
                        break
            if not found:
                partial = self.is_missing(partial, val, metafile)

    def check_hashes(
        self, path: str, pieces: bytes, partial: bytes, pl: int
    ) -> list:
        """
        Check each hash of the provided document to match against metafile.

        Parameters
        ----------
        path : str
            path to content
        pieces : bytes
            metafile hashes
        partial : bytes
            leftover bytes from previous hashes
        pl : int
            size in bytes of the hash contents

        Returns
        -------
        list
            partial bytes and pieces remaining
        """
        matches = count = 0
        with open(path, "br") as contentfile:
            while True:
                diff = pl - len(partial)
                content = contentfile.read(diff)
                if len(content) < pl:
                    if len(content) == 0:
                        break
                    partial += content  # pragma: nocover
                    break  # pragma: nocover
                partial += content
                blok = sha1(partial).digest()  # nosec
                if blok == pieces[: len(blok)]:
                    pieces = pieces[len(blok):]
                    matches += 1
                pieces = pieces[len(blok):]
                partial = bytes()
                count += 1
        if count and matches == 0:
            return []
        return [partial, pieces]

    def is_missing(
        self, partial: bytes, val: dict, metafile: Metadata
    ) -> bytes:
        """
        Run this method if the path is no good or filename doesn't exist.

        Parameters
        ----------
        partial : bytes
            bytes left over from previous hash
        val : dict
            metafile information
        metafile : Metadata
            the metafile

        Returns
        -------
        bytes
            partial bytes from this hash
        """
        pl = metafile.piece_length
        if val["length"] == 0:
            return partial  # pragma: nocover
        length = val["length"]
        while length > 0:
            diff = pl - len(partial)
            if length > diff:
                partial += bytes(diff)
                hash_ = sha1(partial).digest()  # nosec
                metafile.pieces = metafile.pieces[len(hash_):]
                partial = bytes()
                length -= diff
            else:
                partial += bytes(length)
                length -= length
        return partial


def _get_metafiles(metafiles: list) -> None:
    """
    Collect all .torrent meta files from give directory or file.

    Parameters
    ----------
    metafiles : str
        path to a torrent metafile or directory containing torrent metafiles.
    """
    torrent_files = []
    for path in metafiles:
        if os.path.exists(path):
            if os.path.isdir(path):
                for filename in os.listdir(path):
                    if filename.lower().endswith(".torrent"):
                        metafile = Metadata(os.path.join(path, filename))
                        torrent_files.append(metafile)
            elif os.path.isfile(path) and path.lower().endswith(".torrent"):
                metafile = Metadata(path)
                torrent_files.append(metafile)
    return torrent_files


def _index_contents(contents: list) -> dict:
    """
    Collect all of the filenames and their respective paths.

    Parameters
    ----------
    contents : list
        paths to traverse looking for filenames

    Returns
    -------
    dict
        all filenames and their respective paths.
    """
    mapping = {}
    for dirpath in contents:
        mapped = _index_content(dirpath)
        for key, value in mapped.items():
            mapping.setdefault(key, [])
            mapping[key].extend(value)
    return mapping


def _index_content(root: str) -> dict:
    """
    Collect filenames from directory or file.

    Parameters
    ----------
    root : str
        path to search for filenames

    Returns
    -------
    dict
        filenames and their respective paths
    """
    filemap = {}
    if os.path.isfile(root):
        name = os.path.basename(root)
        size = os.path.getsize(root)
        filemap.setdefault(name, [])
        filemap[name].append((root, size))
        return filemap
    if os.path.isdir(root):
        for path in os.listdir(root):
            fullpath = os.path.join(root, path)
            resultmap = _index_content(fullpath)
            for key, value in resultmap.items():
                filemap.setdefault(key, [])
                filemap[key].extend(value)
    return filemap
