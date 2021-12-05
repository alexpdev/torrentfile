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
"""Base and Subclasses for bittorrent meta files.

This module `metafile2` contains classes and functions related
to constructing .torrent files using Bittorrent v2 Protocol

Classes:
    `TorrentFile`: construct .torrent file.
    `TorrentFileV2`: construct .torrent v2 files using provided data.
    `MetaFile` base class for all MetaFile classes.

Constants:
    BLOCK_SIZE (`int`): size of leaf hashes for merkle tree.
    HASH_SIZE (`int`): Length of a sha256 hash.

Notes
-----
Implementation details for Bittorrent Protocol v2.

Metainfo files (also known as .torrent files) are bencoded dictionaries
with the following keys:

"announce":
    The URL of the tracker.

"info":
    This maps to a dictionary, with keys described below.

    "name":
        A display name for the torrent. It is purely advisory.

    "piece length":
        The number of bytes that each logical piece in the peer
        protocol refers to. I.e. it sets the granularity of piece, request,
        bitfield and have messages. It must be a power of two and at least
        6KiB.

    "meta version":
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

    "file tree":
        A tree of dictionaries where dictionary keys represent UTF-8
        encoded path elements. Entries with zero-length keys describe the
        properties of the composed path at that point. 'UTF-8 encoded' in this
        context only means that if the native encoding is known at creation
        time it must be converted to UTF-8. Keys may contain invalid UTF-8
        sequences or characters and names that are reserved on specific
        filesystems. Implementations must be prepared to sanitize them. On
        most platforms path components exactly matching '.' and '..' must be
        sanitized since they could lead to directory traversal attacks and
        conflicting path descriptions. On platforms that require valid UTF-8
        path components this sanitizing step must happen after normalizing
        overlong UTF-8 encodings.
        File is aligned to a piece boundary and occurs in the same order as in
        the file tree. The last piece of each file may be shorter than the
        specified piece length, resulting in an alignment gap.

    "length":
        Length of the file in bytes. Presence of this field indicates
        that the dictionary describes a file, not a directory. Which means
        it must not have any sibling entries.

    "pieces root":
        For non-empty files this is the the root hash of a merkle
        tree with a branching factor of 2, constructed from 16KiB blocks of the
        file. The last block may be shorter than 16KiB. The remaining leaf
        hashes beyond the end of the file required to construct upper layers
        of the merkle tree are set to zero. As of meta version 2 SHA2-256 is
        used as digest function for the merkle tree. The hash is stored in its
        binary form, not as human-readable string.

"piece layers":
    A dictionary of strings. For each file in the file tree that
    is larger than the piece size it contains one string value.
    The keys are the merkle roots while the values consist of concatenated
    hashes of one layer within that merkle tree. The layer is chosen so
    that one hash covers piece length bytes. For example if the piece size is
    16KiB then the leaf hashes are used. If a piece size of 128KiB is used
    then 3rd layer up from the leaf hashes is used. Layer hashes which
    exclusively cover data beyond the end of file, i.e. are only needed to
    balance the tree, are omitted. All hashes are stored in their binary
    format. A torrent is not valid if this field is absent, the contained
    hashes do not match the merkle roots or are not from the correct layer.

> The file tree root dictionary itself must not be a file, i.e. it must not
> contain a zero-length key with a dictionary containing a length key.

--------

From Bittorrent.org Documentation pages.

Metainfo files (also known as .torrent files) are bencoded dictionaries with
the following keys:

announce
    The URL of the tracker.

info

This maps to a dictionary, with keys described below.

All strings in a .torrent file that contains text must be UTF-8 encoded.

## info dictionary

The `name` key maps to a UTF-8 encoded string which is the suggested name to
save the file (or directory) as. It is purely advisory.

`piece length` maps to the number of bytes in each piece the file is split
into. For the purposes of transfer, files are split into fixed-size pieces
which are all the same length except for possibly the last one which may be
truncated. `piece length` is almost always a power of two, most commonly 2 18
= 256 K (BitTorrent prior to version 3.2 uses 2 20 = 1 M as default).

`pieces` maps to a string whose length is a multiple of 20. It is to be
subdivided into strings of length 20, each of which is the SHA1 hash of the
piece at the corresponding index.

There is also a key `length` or a key `files`, but not both or neither. If
`length` is present then the download represents a single file, otherwise it
represents a set of files which go in a directory structure.

In the single file case, `length` maps to the length of the file in bytes.

For the purposes of the other keys, the multi-file case is treated as only
having a single file by concatenating the files in the order they appear in
the files list. The files list is the value `files` maps to, and is a list of
dictionaries containing the following keys:

`length` - The length of the file, in bytes.

`path` - A list of UTF-8 encoded strings corresponding to subdirectory names,
the last of which is the actual file name (a zero length list is an error
case).

In the single file case, the name key is the name of a file, in the muliple
file case, it's the name of a directory.
"""

import logging
import os
from collections.abc import Sequence
from datetime import datetime

import pyben

from . import utils
from .hasher import Feeder, HybridHash, V2Hash
from .version import __version__ as version


class MetaFile:
    """Base Class for all TorrentFile classes.

    Args:
        path (`str`): target path to torrent content.
        announce (`str`): One or more tracker URL's.
        comment (`str`): A comment.
        piece_length (`int`): Size of torrent pieces.
        private (`bool`): For private trackers?
        outfile (`str`): target path to write .torrent file.
        source (`str`): Private tracker source.
    """

    def __init__(self, path=None, announce=None, private=False,
                 source=None, piece_length=None, comment=None,
                 outfile=None, web_seeds=None, align=None):
        """Construct MetaFile superclass and assign local attributes."""
        if not path:
            raise utils.MissingPathError

        # base path to torrent content.
        self.path = path

        # Format piece_length attribute.
        if piece_length:
            self.piece_length = utils.normalize_piece_length(piece_length)
        else:
            self.piece_length = utils.path_piece_length(self.path)

        # Assign announce URL to empty string if none provided.
        if not announce:
            self.announce = ""
            self.announce_list = [[""]]

        # Most torrent clients have editting trackers as a feature.
        elif isinstance(announce, str):
            self.announce = announce
            self.announce_list = [[announce]]
        elif isinstance(announce, Sequence):
            self.announce = announce[0]
            self.announce_list = [[i] for i in announce]

        self.align = align
        self.private = 1 if private else private
        self.web_seeds = web_seeds
        self.source = source
        self.comment = comment
        self.outfile = outfile

        self.meta = {
            "announce": self.announce,
            "announce list": self.announce_list,
            "created by": f"TorrentFile:v{version}",
            "creation date": int(datetime.timestamp(datetime.now())),
            "info": {}
        }

        if self.comment:
            self.meta["info"]["comment"] = self.comment
        if self.private:
            self.meta["info"]["private"] = self.private
        if self.source:
            self.meta["info"]["source"] = self.source
        if self.web_seeds:
            self.meta["url-list"] = self.web_seeds
        self.meta["info"]["name"] = os.path.basename(self.path)
        self.meta["info"]["piece length"] = self.piece_length

    def assemble(self):
        """Overload in subclasses.

        Raises:
            NotImplementedError (`Exception`)
        """
        raise NotImplementedError

    def sort_meta(self):
        """Sort the info and meta dictionaries."""
        meta = self.meta
        meta["info"] = dict(sorted(list(meta["info"].items())))
        meta = dict(sorted(list(meta.items())))
        return meta

    def write(self, outfile=None):
        """Write meta information to .torrent file.

        Args:
            outfile (`str`, default=None): Destination path for .torrent file.

        Returns:
            outfile (`str`): Where the .torrent file was writen.
            meta (`dict`): .torrent meta information.
        """
        if outfile is not None:
            self.outfile = outfile

        if self.outfile is None:
            self.outfile = self.path + ".torrent"

        self.meta = self.sort_meta()
        pyben.dump(self.meta, self.outfile)
        return self.outfile, self.meta


class TorrentFile(MetaFile):
    """Class for creating Bittorrent meta files.

    Construct *Torrentfile* class instance object.

    Args:
        path(`str`): Path to torrent file or directory.
        piece_length(`int`): Size of each piece of torrent data.
        announce(`str` or `list`): One or more tracker URL's.
        private(`int`): 1 if private torrent else 0.
        source(`str`): Source tracker.
        comment(`str`): Comment string.
        outfile(`str`): Path to write metfile to.
    """

    def __init__(self, **kwargs):
        """Construct TorrentFile instance with given keyword args.

        Args:
            kwargs (`dict`): dictionary of keyword args passed to superclass.
        """
        super().__init__(**kwargs)
        logging.debug("Making Bittorrent V1 meta file.")
        self.assemble()

    def assemble(self):
        """Assemble components of torrent metafile.

        Returns:
          `dict`: metadata dictionary for torrent file
        """
        info = self.meta["info"]
        size, filelist = utils.filelist_total(self.path)

        if os.path.isfile(self.path):
            info["length"] = size

        else:
            if not self.align:
                info["files"] = [
                    {
                        "length": os.path.getsize(path),
                        "path": os.path.relpath(path, self.path).split(os.sep),
                    }
                    for path in filelist
                ]
            else:
                files = info["files"] = []
                for path in filelist:
                    total = os.path.getsize(path)
                    remainder = total % self.piece_length
                    files.append({
                        "length": total,
                        "path": os.path.relpath(path, self.path).split(os.sep),
                    })
                    if remainder:
                        files.append({
                            "attr": "p",
                            "length": remainder,
                            "path": [".pad", str(remainder)]
                        })

        pieces = bytearray()
        feeder = Feeder(filelist, self.piece_length, size, align=True)
        for piece in feeder:
            pieces.extend(piece)

        info["pieces"] = pieces


class TorrentFileV2(MetaFile):
    """Class for creating Bittorrent meta v2 files.

    Args:
        path (`str`): Path to torrent file or directory.
        piece_length (`int`): Size of each piece of torrent data.
        announce (`str` or `list`): one or more tracker URL's.
        private (`int`): 1 if private torrent else 0.
        source (`str`): Source tracker.
        comment (`str`): Comment string.
        outfile (`str`): Path to write metfile to.
    """

    def __init__(self, **kwargs):
        """Construct `TorrentFileV2` Class instance from given parameters.

        Args:
            kwargs (`dict`): keywword arguments to pass to superclass.
        """
        super().__init__(**kwargs)
        logging.debug("Create .torrent v2 file.")
        self.piece_layers = {}
        self.hashes = []
        self.assemble()

    def assemble(self):
        """Assemble then return the meta dictionary for encoding.

        Returns:
          meta (`dict`): Metainformation about the torrent.
        """
        info = self.meta["info"]

        if os.path.isfile(self.path):
            info["file tree"] = {info["name"]: self._traverse(self.path)}
            info["length"] = os.path.getsize(self.path)
        else:
            info["file tree"] = self._traverse(self.path)

        info["meta version"] = 2
        self.meta["piece layers"] = self.piece_layers

    def _traverse(self, path):
        """Walk directory tree.

        Args:
            path (`str`): Path to file or directory.
        """
        if os.path.isfile(path):
            # Calculate Size and hashes for each file.
            size = os.path.getsize(path)

            if size == 0:
                return {"": {"length": size}}

            fhash = V2Hash(path, self.piece_length)

            if size > self.piece_length:
                self.piece_layers[fhash.root] = fhash.piece_layer

            return {"": {"length": size, "pieces root": fhash.root}}

        file_tree = {}
        if os.path.isdir(path):

            for base, full in utils.sortfiles(path):
                file_tree[base] = self._traverse(full)

        return file_tree


class TorrentFileHybrid(MetaFile):
    """Construct the Hybrid torrent meta file with provided parameters.

    Args:
        path (`str`): path to torrentfile target.
        announce (`str` or `list`): one or more tracker URL's.
        comment (`str`): Some comment.
        source (`str`): Used for private trackers.
        outfile (`str`): target path to write output.
        private (`bool`): Used for private trackers.
        piece_length (`int`): torrentfile data piece length.
    """

    def __init__(self, **kwargs):
        """Create Bittorrent v1 v2 hybrid metafiles."""
        super().__init__(**kwargs)
        logging.debug("Creating Hybrid torrent file.")
        self.name = os.path.basename(self.path)
        self.hashes = []
        self.piece_layers = {}
        self.pieces = []
        self.files = []
        self.assemble()

    def assemble(self):
        """Assemble the parts of the torrentfile into meta dictionary."""
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

    def _traverse(self, path):
        """Build meta dictionary while walking directory.

        Args:
            path (`str`): Path to target file.
        """
        if os.path.isfile(path):
            fsize = os.path.getsize(path)
            self.files.append(
                {
                    "length": fsize,
                    "path": os.path.relpath(path, self.path).split(os.sep),
                }
            )
            if fsize == 0:
                return {"": {"length": fsize}}

            fhash = HybridHash(path, self.piece_length)
            if fsize > self.piece_length:
                self.piece_layers[fhash.root] = fhash.piece_layer

            self.hashes.append(fhash)
            self.pieces.extend(fhash.pieces)
            if fhash.padding_file:
                self.files.append(fhash.padding_file)

            return {"": {"length": fsize, "pieces root": fhash.root}}

        tree = {}
        if os.path.isdir(path):
            for base, full in utils.sortfiles(path):
                tree[base] = self._traverse(full)

        return tree
