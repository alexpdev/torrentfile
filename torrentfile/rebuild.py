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
import logging
import math
import os
from hashlib import sha1
from pathlib import Path

import pyben

from torrentfile.hasher import HasherV2
from torrentfile.mixins import CbMixin, ProgMixin
from torrentfile.utils import copypath

logger = logging.getLogger(__name__)
SHA1 = 20


class PathNode:
    """
    Base class representing information regarding a file included in torrent.
    """

    def __init__(
        self,
        start: int = None,
        stop: int = None,
        full: str = None,
        filename: str = None,
        path: str = None,
        length: int = None,
    ):
        """
        Hold file information that contributes to the contents of torrent.

        Parameters
        ----------
        start : int, optional
            where the piece starts, by default None
        stop : int, optional
            where the piece ends, by default None
        full : str, optional
            full path, by default None
        filename : str, optional
            filename, by default None
        path : str, optional
            parent path, by default None
        length : int, optional
            size, by default None
        """
        self.path = path
        self.start = start
        self.stop = stop
        self.length = length
        self.filename = filename
        self.full = full

    def get_part(self, path: str) -> bytes:
        """
        Extract the part of the file needed to complete the hash.

        Parameters
        ----------
        path : str
            filesystem path location of file.

        Returns
        -------
        bytes
            part of the file's contents
        """
        with open(path, "rb") as fd:
            if self.start:
                fd.seek(self.start)
            if self.stop != -1:
                partial = fd.read(self.stop - self.start)
            else:
                partial = fd.read()
        return partial

    def __len__(self) -> int:
        """
        Return size of the file.

        Returns
        -------
        int
            total size
        """
        return self.length


class PieceNode:
    """
    Base class representing a single SHA1 hash block of data from a torrent.
    """

    def __init__(self, piece: bytes):
        """
        Store information about an individual SHA1 hash for a torrent file.

        _extended_summary_

        Parameters
        ----------
        piece : bytes
            SHA1 hash bytes
        """
        self.piece = piece
        self.paths = []
        self.result = None
        self.dest = None

    def append(self, pathnode: PathNode):
        """
        Append the path argument to the paths list attribute.

        Parameters
        ----------
        pathnode : PathNode
            the pathnode
        """
        self.paths.append(pathnode)

    def _find_matches(self, filemap: dict, paths: list, data: bytes) -> bool:
        """
        Gather relavent sections of the files in the list and check the hash.

        Parameters
        ----------
        filemap : dict
            dictionary containing filename and path details
        paths : list
            list of pathnodes
        data : bytes
            raw file contents

        Returns
        -------
        bool
            success state
        """
        if not paths:
            piece_hash = sha1(data).digest()  # nosec
            return piece_hash == self.piece
        pathnode = paths[0]
        filename = pathnode.filename
        if filename not in filemap:
            return False  # pragma: nocover
        for loc, size in filemap[filename]:
            if size != len(pathnode):
                continue
            partial = pathnode.get_part(loc)
            val = self._find_matches(filemap, paths[1:], data + partial)
            if val:
                dest_path = os.path.join(self.dest, pathnode.full)
                copypath(loc, dest_path)
            return val
        return False

    def find_matches(self, filemap: dict, dest: str) -> bool:
        """
        Find the matching files for each path in the node.

        Parameters
        ----------
        filemap : dict
            filename and details
        dest : str
            target destination path

        Returns
        -------
        bool
            success status
        """
        self.dest = dest
        self.result = self._find_matches(filemap, self.paths[:], bytes())
        return self.result


class Metadata(CbMixin, ProgMixin):
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
        self.name = None
        self.piece_length = 1
        self.meta_version = 1
        self.pieces = b""
        self.piece_nodes = []
        self.length = 0
        self.files = []
        self.filenames = set()
        self.extract()
        if self.meta_version == 2:
            self.num_pieces = len(self.filenames)
        else:
            self.num_pieces = math.ceil(len(self.pieces) / SHA1)

    def extract(self):
        """
        Decode and extract information for the .torrent file.
        """
        meta = pyben.load(self.path)
        info = meta["info"]
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

    def _map_pieces(self):
        """
        Create PathNode and PieceNode details for each piece in the torrent.
        """
        total_pieces = len(self.pieces) // SHA1
        remainder = file_index = 0
        current = {}
        for i in range(total_pieces):
            begin = SHA1 * i
            piece = PieceNode(self.pieces[begin: begin + SHA1])
            target = self.piece_length
            if remainder:
                start = current["length"] - remainder
                if remainder < target:
                    stop = -1
                    target -= remainder
                    remainder = 0
                    file_index += 1
                else:
                    stop = start + target
                    remainder -= target
                    target -= target
                pathnode = PathNode(start=start, stop=stop, **current)
                piece.append(pathnode)
            while target > 0 and file_index < len(self.files):
                start = 0
                current = self.files[file_index]
                size = current["length"]
                if size < target:
                    stop = -1
                    target -= size
                    file_index += 1
                else:
                    stop = target
                    remainder = size - target
                    target = 0
                pathnode = PathNode(start=start, stop=stop, **current)
                piece.append(pathnode)
            self.piece_nodes.append(piece)

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

    def _match_v1(self, filemap: dict, dest: str):
        """
        Check each of the nodes against the filemap dictionary for matches.

        Parameters
        ----------
        filemap : dict
            filenames and filesystem information
        dest : str
            target destination path
        """
        self._map_pieces()
        copied = []
        for piece_node in self.piece_nodes:
            paths = piece_node.paths
            if len(paths) == 1 and paths[0].path in copied:
                self._update()
                continue
            if piece_node.find_matches(filemap, dest):
                for pathnode in paths:
                    if pathnode.path not in copied:
                        copied.append(pathnode.path)
                        dest_path = os.path.join(dest, pathnode.path)
                        self._update()
                        self.cb(pathnode.path, dest_path, self.num_pieces)

    def _match_v2(self, filemap: dict, dest: str):
        """
        Rebuild method for torrent v2 files.

        Parameters
        ----------
        filemap : dict
            filesystem information
        dest : str
            destiantion path
        """
        for entry in self.files:
            filename = entry["filename"]
            length = entry["length"]
            if filename not in filemap:
                continue  # pragma: nocover
            paths = filemap[filename]
            for path, size in paths:
                if size == length:
                    hasher = HasherV2(path, self.piece_length, True)
                    if entry["root"] == hasher.root:
                        dest_path = os.path.join(dest, entry["full"])
                        copypath(entry["path"], dest_path)
                        self._update()
                        self.cb(path, dest_path, self.num_pieces)
                        break

    def rebuild(self, filemap: dict, dest: str):
        """
        Rebuild torrent file contents from filemap at dest.

        Searches through the contents of the meta file and compares filenames
        with those in the filemap dict, and if found checks their contents,
        and copies them to the destination path.

        Parameters
        ----------
        filemap : dict
            filesystem information
        dest : str
            destiantion path
        """
        self._prog = None
        if self.meta_version == 2:
            self._match_v2(filemap, dest)
        else:
            self._match_v1(filemap, dest)
        if self._prog is not None:
            self.prog_close()

    def _update(self):
        """Start and updating the progress bar."""
        if self._prog is None:
            self._prog = True
            self.prog_start(self.num_pieces, self.name, unit="piece")
        self.prog_update(1)


class Assembler(CbMixin):
    """
    Does most of the work in attempting the structure of torrentfiles.

    Requires three paths as arguments.
    - torrent metafile or directory containing multiple meta files
    - directory containing the contents of meta file
    - directory where torrents will be re-assembled
    """

    def __init__(self, metafiles: list, contents: list, dest: str):
        """
        Reassemble given torrent file from given cli arguments.

        Rebuild metafiles and contents into their original directory
        structure as much as possible in the destination directory.
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
        Metadata.set_callback(self._callback)
        self.counter = 0
        self._lastlog = None
        self.contents = contents
        self.dest = dest
        self.meta_paths = metafiles
        self.metafiles = self._get_metafiles()
        filenames = set()
        for meta in self.metafiles:
            filenames |= meta.filenames
        self.filemap = _index_contents(self.contents, filenames)

    def _callback(self, filename: str, dest: str, num_pieces: int):
        """
        Run the callback functions associated with Mixin for copied files.

        Parameters
        ----------
        filename : str
            filename
        dest : str
            destination path
        num_pieces : int
            number of hash pieces
        """
        self.counter += 1
        message = f"Matched:{num_pieces} {filename} -> {dest}"
        if message != self._lastlog:
            self._lastlog = message
            logger.debug(message)

    def assemble_torrents(self):
        """
        Assemble collection of torrent files into original structure.

        Returns
        -------
        int
            number of files copied
        """
        for metafile in self.metafiles:
            logger.info(
                "#%s Searching contents for %s", self.counter, metafile.name
            )
            self.rebuild(metafile)
        return self.counter

    def rebuild(self, metafile: Metadata) -> None:
        """
        Build the torrent file structure from contents of directory.

        Traverse contents dir and compare discovered files
        with files listed in torrent metadata and copy
        the matches to the destination directory respecting folder
        structures along the way.
        """
        metafile.rebuild(self.filemap, self.dest)

    def _iter_files(self, path: str) -> list:
        """
        Iterate through metfiles directory createing Metafile objects.

        Parameters
        ----------
        path : str
            fs path

        Returns
        -------
        list
            list of Metadata Object
        """
        metafiles = []
        for filename in os.listdir(path):
            if filename.lower().endswith(".torrent"):
                try:
                    meta = Metadata(os.path.join(path, filename))
                    metafiles.append(meta)
                except ValueError:  # pragma: nocover
                    self.counter -= 1
        return metafiles

    def _get_metafiles(self) -> list:
        """
        Collect all .torrent meta files from given directory or file.

        Returns
        -------
        list
            metafile objects
        """
        metafiles = []
        for path in self.meta_paths:
            if os.path.exists(path):
                if os.path.isdir(path):
                    metafiles += self._iter_files(path)
                elif path.lower().endswith(".torrent"):
                    meta = Metadata(path)
                    metafiles.append(meta)
        return metafiles


def _index_contents(contents: list, filenames: set) -> dict:
    """
    Collect all of the filenames and their respective paths.

    Parameters
    ----------
    contents : list
        paths to traverse looking for filenames
    filenames : set
        set of filenames to look for

    Returns
    -------
    dict
        all filenames and their respective paths.
    """
    mapping = {}
    for dirpath in contents:
        mapped = _index_content(dirpath, filenames)
        for key, value in mapped.items():
            mapping.setdefault(key, [])
            mapping[key].extend(value)
    return mapping


def _index_content(root: str, filenames: set) -> dict:
    """
    Collect filenames from directory or file.

    Parameters
    ----------
    root : str
        path to search for filenames
    filenames : set
        set of filenames to search for

    Returns
    -------
    dict
        filenames and their respective paths
    """
    filemap = {}
    if os.path.isfile(root):
        name = os.path.basename(root)
        if name in filenames:
            size = os.path.getsize(root)
            filemap.setdefault(name, [])
            filemap[name].append((root, size))
        return filemap
    if os.path.isdir(root):
        for path in os.listdir(root):
            fullpath = os.path.join(root, path)
            resultmap = _index_content(fullpath, filenames)
            for key, value in resultmap.items():
                filemap.setdefault(key, [])
                filemap[key].extend(value)
    return filemap
