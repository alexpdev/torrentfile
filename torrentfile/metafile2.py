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
Torrent meta file procedures for Bittorrent v2.

This module `metafile2` contains classes and functions related
to constructing .torrent files using Bittorrent v2 Protocol

Classes:
    `TorrentFileV2`: construct .torrent files using provided data.
    `FileHash`: Calculates leaf hashes and root hashes for torrent contents.

Constants:
    BLOCK_SIZE (`int`): size of leaf hashes for merkle tree.
    HASH_SIZE (`int`): Length of a sha256 hash.

## Notes
--------
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
"""

import logging
import math
import os
from hashlib import sha256

from .metabase import MetaFile
from .utils import sortfiles

BLOCK_SIZE = 2 ** 14  # 16KiB
HASH_SIZE = 32


class TorrentFileV2(MetaFile):
    """Class for creating Bittorrent meta v2 files.

    Args:
        path (`str`): Path to torrent file or directory.
        piece_length (`int`): Size of each piece of torrent data.
        announce (`str`): Tracker URL.
        announce_list ('list`): List of additional trackers.
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
        self.meta = self.assemble()

    def _assemble_infodict(self):
        """Create info dictionary for .torrent meta v2 file.

        Returns:
          info (`dict`): Info dictionary containing torrent metadata.
        """
        name = os.path.basename(self.path)
        info = {}
        # include comment in info dictionary.
        if self.announce_list:
            info["announce list"] = self.announce_list

        if self.comment:
            info["comment"] = self.comment

        if os.path.isfile(self.path):
            logging.debug("'path' points to a single file.")
            info["file tree"] = {name: self._traverse(self.path)}
            info["length"] = os.path.getsize(self.path)
        else:
            logging.debug("'path' points to a directory.")
            info["file tree"] = self._traverse(self.path)

        info["name"] = name
        info["piece length"] = self.piece_length
        # Bittorrent Protocol v2
        info["meta version"] = 2

        if self.private:
            info["private"] = 1
            logging.debug("Torrent file will be marked as private.")
        if self.source:
            info["source"] = self.source
        logging.debug("Filled Info Dictionary.")

        return info

    def assemble(self):
        """Assemble then return the meta dictionary for encoding.

        Returns:
          meta (`dict`): Metainformation about the torrent.
        """
        logging.debug("Continue filling meta dictionary for .torrent file.")
        meta = self.apply_constants()
        # assemble info dictionary and assign it to info key in meta
        meta["info"] = self._assemble_infodict()

        meta["piece layers"] = self.piece_layers
        return meta

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

            for base, full in sortfiles(path):
                file_tree[base] = self._traverse(full)

        return file_tree


def merkle_root(pieces):
    """Generate root hash of a merkle Tree with input as leaves."""
    while len(pieces) > 1:
        pieces = [sha256(x + y).digest() for x, y in zip(*[iter(pieces)] * 2)]
    return pieces[0]


class V2Hash:
    """Calculate the root hash and piece layers for file contents.

    Iterates over 16KiB blocks of data from given file, hashes the data,
    then creates a hash tree from the individual block hashes until size of
    hashed data equals the piece-length.  Then continues the hash tree until
    root hash is calculated.

    Args:
      path (`str`): Path to file.
      piece_length (`int`): Size of layer hashes pieces.
    """

    def __init__(self, path, piece_length):
        """Calculate and store hash information for specific file."""
        self.path = path
        self.root = None
        self.piece_layer = None
        self.layer_hashes = []
        self.piece_length = piece_length
        self.num_blocks = piece_length // BLOCK_SIZE
        logging.debug("Hashing v2: %s", self.path)

        with open(self.path, "rb") as fd:
            self.process_file(fd)

    def process_file(self, fd):
        """Calculate hashes over 16KiB chuncks of file content.

        Args:
            fd (`str`): Opened file in read mode.
        """
        while True:
            total = 0
            blocks = []
            leaf = bytearray(BLOCK_SIZE)
            # generate leaves of merkle tree
            for _ in range(self.num_blocks):
                size = fd.readinto(leaf)
                total += size
                if not size:
                    break
                blocks.append(sha256(leaf[:size]).digest())
            # blocks is empty mean eof
            if not blocks:
                break
            if len(blocks) != self.num_blocks:
                if not self.layer_hashes:
                    next_pow_2 = 1 << int(math.log2(total) + 1)
                    remaining = ((next_pow_2 - total) // BLOCK_SIZE) + 1
                else:
                    remaining = self.num_blocks - size
                padding = [bytes(HASH_SIZE) for _ in range(remaining)]
                blocks.extend(padding)
            # if the file is smaller than piece length
            layer_hash = merkle_root(blocks)
            self.layer_hashes.append(layer_hash)
        self._calculate_root()

    def _calculate_root(self):
        """Calculate root hash for the target file."""
        self.piece_layer = b"".join(self.layer_hashes)
        if len(self.layer_hashes) > 1:
            next_pow_2 = 1 << int(math.log2(len(self.layer_hashes)) + 1)
            remainder = next_pow_2 - len(self.layer_hashes)
            pad_piece = [bytes(HASH_SIZE) for _ in range(self.num_blocks)]
            for _ in range(remainder):
                self.layer_hashes.append(merkle_root(pad_piece))
        self.root = merkle_root(self.layer_hashes)
