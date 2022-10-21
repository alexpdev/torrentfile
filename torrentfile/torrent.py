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
Classes and procedures pertaining to the creation of torrent meta files.

Classes
-------

- `TorrentFile`
    construct .torrent file.

- `TorrentFileV2`
    construct .torrent v2 files using provided data.

- `MetaFile`
    base class for all MetaFile classes.

Constants
---------

- BLOCK_SIZE : int
    size of leaf hashes for merkle tree.

- HASH_SIZE : int
    Length of a sha256 hash.

Bittorrent V2
-------------

**From Bittorrent.org Documentation pages.**

*Implementation details for Bittorrent Protocol v2.*

!!!Note
    All strings in a .torrent file that contain text must be UTF-8 encoded.

### Meta Version 2 Dictionary:

- "announce":
    The URL of the tracker.

- "info":
    This maps to a dictionary, with keys described below.

    - "name":
        A display name for the torrent. It is purely advisory.

    - "piece length":
        The number of bytes that each logical piece in the peer
        protocol refers to. I.e. it sets the granularity of piece, request,
        bitfield and have messages. It must be a power of two and at least
        6KiB.

    - "meta version":
        An integer value, set to 2 to indicate compatibility
        with the current revision of this specification. Version 1 is not
        assigned to avoid confusion with BEP3. Future revisions will only
        increment this issue to indicate an incompatible change has been made,
        for example that hash algorithms were changed due to newly discovered
        vulnerabilities. Lementations must check this field first and indicate
        that a torrent is of a newer version than they can handle before
        performing other idations which may result in more general messages
        about invalid files. Files are mapped into this piece address space so
        that each non-empty

    - "file tree":
        A tree of dictionaries where dictionary keys represent UTF-8
        encoded path elements. Entries with zero-length keys describe the
        properties of the composed path at that point. 'UTF-8 encoded'
        context only means that if the native encoding is known at creation
        time it must be converted to UTF-8. Keys may contain invalid UTF-8
        sequences or characters and names that are reserved on specific
        filesystems. Implementations must be prepared to sanitize them. On
        platforms path components exactly matching '.' and '..' must be
        sanitized since they could lead to directory traversal attacks and
        conflicting path descriptions. On platforms that require UTF-8
        path components this sanitizing step must happen after normalizing
        overlong UTF-8 encodings.
        File is aligned to a piece boundary and occurs in same order as
        the file tree. The last piece of each file may be shorter than the
        specified piece length, resulting in an alignment gap.

    - "length":
        Length of the file in bytes. Presence of this field indicates
        that the dictionary describes a file, not a directory. Which means
        it must not have any sibling entries.

    - "pieces root":
        For non-empty files this is the the root hash of a merkle
        tree with a branching factor of 2, constructed from 16KiB blocks
        of the file. The last block may be shorter than 16KiB. The
        remaining leaf hashes beyond the end of the file required to
        construct upper layers of the merkle tree are set to zero. As of
        meta version 2 SHA2-256 is used as digest function for the merkle
        tree. The hash is stored in its binary form, not as human-readable
        string.

- "piece layers":
    A dictionary of strings. For each file in the file tree that
    is larger than the piece size it contains one string value.
    The keys are the merkle roots while the values consist of concatenated
    hashes of one layer within that merkle tree. The layer is chosen so
    that one hash covers piece length bytes. For example if the piece
    size is 16KiB then the leaf hashes are used. If a piece size of
    128KiB is used then 3rd layer up from the leaf hashes is used. Layer
    hashes which exclusively cover data beyond the end of file, i.e.
    are only needed to balance the tree, are omitted. All hashes are
    stored in their binary format. A torrent is not valid if this field is
    absent, the contained hashes do not match the merkle roots or are
    not from the correct layer.

!!!important
    The file tree root dictionary itself must not be a file,
    i.e. it must not contain a zero-length key with a dictionary containing
    a length key.

Bittorrent V1
-------------

### v1 meta-dictionary

- announce:
    The URL of the tracker.

- info:
    This maps to a dictionary, with keys described below.

    - `name`:
        maps to a UTF-8 encoded string which is the suggested name to
        save the file (or directory) as. It is purely advisory.

    - `piece length`:
        maps to the number of bytes in each piece the file is split
        into. For the purposes of transfer, files are split into
        fixed-size pieces which are all the same length except for
        possibly the last one which may be truncated.

    - `piece length`:
        is almost always a power of two, most commonly 2^18 = 256 K

    - `pieces`:
        maps to a string whose length is a multiple of 20. It is to be
        subdivided into strings of length 20, each of which is the SHA1
        hash of the piece at the corresponding index.

    - `length`:
        In the single file case, maps to the length of the file in bytes.

    - `files`:
        If present then the download represents a single file, otherwise it
        represents a set of files which go in a directory structure.
        For the purposes of the other keys, the multi-file case is treated
        as only having a single file by concatenating the files in the order
        they appear in the files list. The files list is the value `files`
        maps to, and is a list of dictionaries containing the following keys:

        - `path`:
            A list of UTF-8 encoded strings corresponding to subdirectory
            names, the last of which is the actual file name

        - `length`:
            Maps to the length of the file in bytes.

    - `length`:
        Only present if the content is a single file. Maps to the length
        of the file in bytes.

!!!Note
    In the single file case, the name key is the name of a file,
    in the muliple file case, it's the name of a directory.
"""

import logging
import os
from collections.abc import Sequence
from datetime import datetime

import pyben

from torrentfile import utils
from torrentfile.hasher import FileHasher, Hasher, HasherHybrid, HasherV2
from torrentfile.mixins import ProgMixin
from torrentfile.version import __version__ as version

logger = logging.getLogger(__name__)


class MetaFile:
    """
    Base Class for all TorrentFile classes.

    Parameters
    ----------
    path : str
        target path to torrent content.  Default: None
    announce : str
        One or more tracker URL's.  Default: None
    comment : str
        A comment.  Default: None
    piece_length : int
        Size of torrent pieces.  Default: None
    private : bool
        For private trackers.  Default: None
    outfile : str
        target path to write .torrent file. Default: None
    source : str
        Private tracker source. Default: None
    progress : str
        level of progress bar displayed  Default: "1"
    cwd : bool
        If True change default save location to current directory
    httpseeds : list
        one or more web addresses where torrent content can be found.
    url_list : list
        one or more web addressess where torrent content exists.
    content : str
        alias for 'path' arg.
    meta_version : int
        indicates which Bittorrent protocol to use for hashing content
    """

    hasher = None

    @classmethod
    def set_callback(cls, func):
        """
        Assign a callback function for the Hashing class to call for each hash.

        Parameters
        ----------
        func : function
            The callback function which accepts a single paramter.
        """
        if "hasher" in vars(cls) and vars(cls)["hasher"]:
            cls.hasher.set_callback(func)

    def __init__(
        self,
        path=None,
        announce=None,
        comment=None,
        piece_length=None,
        private=False,
        outfile=None,
        source=None,
        progress=1,
        cwd=False,
        httpseeds=None,
        url_list=None,
        content=None,
        meta_version=None,
        **_,
    ):
        """
        Construct MetaFile superclass and assign local attributes.
        """
        self.private = private
        self.cwd = cwd
        self.outfile = outfile
        self.progress = int(progress)
        self.comment = comment
        self.source = source
        self.meta_version = meta_version

        if content:
            path = content
        if not path:
            if announce and len(announce) > 1 and os.path.exists(announce[-1]):
                path = announce[-1]
                announce = announce[:-1]
            elif url_list and os.path.exists(url_list[-1]):
                path = url_list[-1]
                url_list = url_list[:-1]
            elif httpseeds and os.path.exists(httpseeds[-1]):
                path = httpseeds[-1]
                httpseeds = httpseeds[:-1]
            else:
                raise utils.MissingPathError("Path to content is required.")

        # base path to torrent content.
        self.path = path

        logger.debug("path parameter found %s", path)

        # Format piece_length attribute.
        if piece_length:
            self.piece_length = utils.normalize_piece_length(piece_length)
            logger.debug("piece length parameter found %s", piece_length)
        else:
            self.piece_length = utils.path_piece_length(self.path)
            logger.debug("piece length calculated %s", self.piece_length)

        # Assign announce URL to empty string if none provided.
        if not announce:
            self.announce, self.announce_list = "", [[""]]

        # Most torrent clients have editting trackers as a feature.
        elif isinstance(announce, str):
            self.announce, self.announce_list = announce, [[announce]]

        elif isinstance(announce, Sequence):
            self.announce, self.announce_list = announce[0], [announce]

        self.meta = {
            "announce": self.announce,
            "announce-list": self.announce_list,
            "created by": f"TorrentFile_v{version}",
            "creation date": int(datetime.timestamp(datetime.now())),
            "info": {},
        }
        if comment:
            self.meta["info"]["comment"] = comment
            logger.debug("comment parameter found %s", comment)
        if private:
            self.meta["info"]["private"] = 1
            logger.debug("private parameter triggered")
        if source:
            self.meta["info"]["source"] = source
            logger.debug("source parameter found %s", source)
        if url_list:
            self.meta["url-list"] = url_list
            logger.debug("url list parameter found %s", str(url_list))
        if httpseeds:
            self.meta["httpseeds"] = httpseeds
            logger.debug("httpseeds parameter found %s", str(httpseeds))
        self.meta["info"]["piece length"] = self.piece_length

        self.meta_version = meta_version
        parent, self.name = os.path.split(self.path)
        if not self.name:
            self.name = os.path.basename(parent)
        self.meta["info"]["name"] = self.name

    def assemble(self):
        """
        Overload in subclasses.

        Raises
        ------
        Exception
            NotImplementedError
        """
        raise NotImplementedError

    def sort_meta(self):
        """Sort the info and meta dictionaries."""
        logger.debug("sorting dictionary keys")
        meta = self.meta
        meta["info"] = dict(sorted(list(meta["info"].items())))
        meta = dict(sorted(list(meta.items())))
        return meta

    def write(self, outfile=None) -> tuple:
        """
        Write meta information to .torrent file.

        Final step in the torrent file creation process.
        After hashing and sorting every piece of content
        write the contents to file using the bencode encoding.

        Parameters
        ----------
        outfile : str
            Destination path for .torrent file. default=None

        Returns
        -------
        outfile : str
            Where the .torrent file was writen.
        meta : dict
            .torrent meta information.
        """
        if outfile:
            self.outfile = outfile
        elif self.outfile:
            pass
        else:
            self.outfile = os.path.join(os.getcwd(), self.name) + ".torrent"
        if str(self.outfile)[-1] in "\\/":
            self.outfile = self.outfile + (self.name + ".torrent")
        self.meta = self.sort_meta()
        try:
            pyben.dump(self.meta, self.outfile)
        except PermissionError as excp:
            logger.error(
                "Permission Denied: Could not write to %s", self.outfile
            )
            raise PermissionError from excp
        return self.outfile, self.meta


class TorrentFile(MetaFile, ProgMixin):
    """
    Class for creating Bittorrent meta files.

    Construct *Torrentfile* class instance object.

    Parameters
    ----------
    **kwargs : dict
        Dictionary containing torrent file options.
    """

    hasher = Hasher

    def __init__(self, **kwargs):
        """
        Construct TorrentFile instance with given keyword args.

        Parameters
        ----------
        **kwargs : dict
            dictionary of keyword args passed to superclass.
        """
        super().__init__(**kwargs)
        logger.debug("Assembling bittorrent v1 torrent file")
        self.assemble()

    def assemble(self):
        """
        Assemble components of torrent metafile.

        Returns
        -------
        dict
            metadata dictionary for torrent file
        """
        info = self.meta["info"]
        size, filelist = utils.filelist_total(self.path)
        if os.path.isfile(self.path):
            info["length"] = size
        else:
            info["files"] = [
                {
                    "length": os.path.getsize(path),
                    "path": os.path.relpath(path, self.path).split(os.sep),
                }
                for path in filelist
            ]
        pieces = bytearray()

        feeder = Hasher(filelist, self.piece_length, self.progress)
        for piece in feeder:
            pieces.extend(piece)

        info["pieces"] = pieces


class TorrentFileV2(MetaFile, ProgMixin):
    """
    Class for creating Bittorrent meta v2 files.

    Parameters
    ----------
    **kwargs : dict
        Keyword arguments for torrent file options.
    """

    hasher = HasherV2

    def __init__(self, **kwargs):
        """
        Construct `TorrentFileV2` Class instance from given parameters.

        Parameters
        ----------
        **kwargs : dict
            keywword arguments to pass to superclass.
        """
        super().__init__(**kwargs)
        logger.debug("Assembling bittorrent v2 torrent file")
        self.piece_layers = {}
        self.hashes = []
        self.total = len(utils.get_file_list(self.path))
        self.assemble()

    def assemble(self):
        """
        Assemble then return the meta dictionary for encoding.

        Returns
        -------
        meta : dict
            Metainformation about the torrent.
        """
        info = self.meta["info"]
        if os.path.isfile(self.path):
            info["file tree"] = {info["name"]: self._traverse(self.path)}
            info["length"] = os.path.getsize(self.path)
            self.prog_update(info["length"])
        else:
            info["file tree"] = self._traverse(self.path)

        info["meta version"] = 2
        self.meta["piece layers"] = self.piece_layers

    def _traverse(self, path: str) -> dict:
        """
        Walk directory tree.

        Parameters
        ----------
        path : str
            Path to file or directory.
        """
        if os.path.isfile(path):
            # Calculate Size and hashes for each file.
            size = os.path.getsize(path)

            if size == 0:
                return {"": {"length": size}}

            logger.debug("Hashing %s", str(path))
            fhash = HasherV2(path, self.piece_length, self.progress)

            if size > self.piece_length:
                self.piece_layers[fhash.root] = fhash.piece_layer
            return {"": {"length": size, "pieces root": fhash.root}}

        file_tree = {}
        if os.path.isdir(path):
            for name in sorted(os.listdir(path)):
                file_tree[name] = self._traverse(os.path.join(path, name))
        return file_tree


class TorrentFileHybrid(MetaFile, ProgMixin):
    """
    Construct the Hybrid torrent meta file with provided parameters.

    Parameters
    ----------
    **kwargs : dict
        Keyword arguments for torrent options.
    """

    hasher = HasherHybrid

    def __init__(self, **kwargs):
        """
        Create Bittorrent v1 v2 hybrid metafiles.
        """
        super().__init__(**kwargs)
        logger.debug("Assembling bittorrent Hybrid file")
        self.name = os.path.basename(self.path)
        self.hashes = []
        self.piece_layers = {}
        self.pieces = []
        self.files = []
        self.total = len(utils.get_file_list(self.path))
        self.assemble()

    def assemble(self):
        """
        Assemble the parts of the torrentfile into meta dictionary.
        """
        info = self.meta["info"]
        info["meta version"] = 2

        if os.path.isfile(self.path):
            info["file tree"] = {self.name: self._traverse(self.path)}
            info["length"] = os.path.getsize(self.path)

        else:
            info["file tree"] = self._traverse(self.path)
            info["files"] = self.files

        info["pieces"] = b"".join(self.pieces)
        self.meta["piece layers"] = self.piece_layers
        return info

    def _traverse(self, path: str) -> dict:
        """
        Build meta dictionary while walking directory.

        Parameters
        ----------
        path : str
            Path to target file.
        """
        if os.path.isfile(path):
            file_size = os.path.getsize(path)

            self.files.append(
                {
                    "length": file_size,
                    "path": os.path.relpath(path, self.path).split(os.sep),
                }
            )

            if file_size == 0:
                return {"": {"length": file_size}}

            logger.debug("Hashing %s", str(path))
            file_hash = HasherHybrid(path, self.piece_length, self.progress)
            self.prog_update(file_size)

            if file_size > self.piece_length:
                self.piece_layers[file_hash.root] = file_hash.piece_layer

            self.hashes.append(file_hash)
            self.pieces.extend(file_hash.pieces)

            if file_hash.padding_file:
                self.files.append(file_hash.padding_file)

            return {"": {"length": file_size, "pieces root": file_hash.root}}

        tree = {}
        if os.path.isdir(path):
            for name in sorted(os.listdir(path)):
                tree[name] = self._traverse(os.path.join(path, name))
        return tree


class TorrentAssembler(MetaFile):
    """
    Assembler class for Bittorrent version 2 and hybrid meta files.

    This differs from the TorrentFileV2 and TorrentFileHybrid, because
    it can be used as an iterator and works for both versions.

    Parameters
    ----------
    **kwargs : dict
        Keyword arguments for torrent options.
    """

    hasher = FileHasher

    def __init__(self, **kwargs):
        """
        Create Bittorrent v1 v2 hybrid metafiles.
        """
        super().__init__(**kwargs)
        logger.debug("Assembling bittorrent Hybrid file")
        self.name = os.path.basename(self.path)
        self.hashes = []
        self.piece_layers = {}
        self.pieces = bytearray()
        self.files = []
        self.hybrid = self.meta_version == "3"
        self.total = len(utils.get_file_list(self.path))
        self.assemble()

    def assemble(self):
        """
        Assemble the parts of the torrentfile into meta dictionary.
        """
        info = self.meta["info"]
        info["meta version"] = 2

        if os.path.isfile(self.path):
            info["file tree"] = {self.name: self._traverse(self.path)}
            info["length"] = os.path.getsize(self.path)

        else:
            info["file tree"] = self._traverse(self.path)
            if self.hybrid:
                info["files"] = self.files

        if self.hybrid:
            info["pieces"] = self.pieces
        self.meta["piece layers"] = self.piece_layers
        return info

    def _traverse(self, path: str) -> dict:
        """
        Build meta dictionary while walking directory.

        Parameters
        ----------
        path : str
            Path to target file.
        """
        if os.path.isfile(path):
            file_size = os.path.getsize(path)
            if self.hybrid:
                self.files.append(
                    {
                        "length": file_size,
                        "path": os.path.relpath(path, self.path).split(os.sep),
                    }
                )

            if file_size == 0:
                return {"": {"length": file_size}}

            logger.debug("Hashing %s", str(path))
            hasher = FileHasher(
                path, self.piece_length, progress=True, hybrid=self.hybrid
            )
            layers = bytearray()
            for result in hasher:
                if self.hybrid:
                    layer_hash, piece = result
                    self.pieces.extend(piece)
                else:
                    layer_hash = result
                layers.extend(layer_hash)
            if file_size > self.piece_length:
                self.piece_layers[hasher.root] = layers
            if self.hybrid and hasher.padding_file:
                self.files.append(hasher.padding_file)

            return {"": {"length": file_size, "pieces root": hasher.root}}

        tree = {}
        if os.path.isdir(path):
            for name in sorted(os.listdir(path)):
                tree[name] = self._traverse(os.path.join(path, name))
        return tree
