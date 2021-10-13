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
Classes and procedures for making Bittorrent metafiles.

Creating .torrent files that support both Bittorrent v1 & v2
metadata structure and hashes simultaneously. This module was partly
influenced by "bep_0052_torrent_creator".

Classes:
    TorrentFileHybrid
    Hasher
"""

import math
import os
from datetime import datetime
from hashlib import sha1, sha256  # nosec

import pyben

from .utils import MetaFile, path_piece_length, sortfiles

BLOCK_SIZE = 2 ** 14
HASH_SIZE = 32


class TorrentFileHybrid(MetaFile):
    """Create Bittorrent v1 v2 hybrid metafiles."""

    def __init__(self, **kwargs):
        """
        Construct the Hybrid torrent meta file with provided parameters.

        Args:
            path (`str`): path to torrentfile target.
            announce (`str`): Tracker URL.
            announce_list (`list`): Additional tracker URLs.
            comment (`str`): Some comment.
            source (`str`): Used for private trackers.
            outfile (`str`): target path to write output.
            private (`bool`): Used for private trackers.
            piece_length (`int`): torrentfile data piece length.
        """
        super().__init__(**kwargs)
        self.name = os.path.basename(self.path)[-1]
        self.hashes = []
        self.piece_layers = {}
        self.pieces = []
        self.files = []
        self.meta = self.assemble()

    def assemble(self):
        """Assemble the parts of the torrentfile into meta dictionary."""
        meta = {"announce": self.announce}

        meta["creation date"] = int(datetime.timestamp(datetime.now()))
        meta["created by"] = "torrentfile"

        meta["info"] = self._assemble_infodict()

        meta["pieces"] = b"".join(self.pieces)
        meta["piece_layers"] = self.piece_layers

        return meta

    def _assemble_infodict(self):
        """
        Assemble info dictionary contained in meta info.

        Returns:
            info(`dict`): Info dictionary.
        """
        if not self.piece_length:
            self.piece_length = path_piece_length(self.path)

        info = {
            "name": self.name,
            "meta version": 2,
            "piece length": self.piece_length
        }

        if self.announce_list:
            info["announce list"] = self.announce_list

        if os.path.isfile(self.path):
            info["file tree"] = {self.name: self._traverse(self.path)}
            info["length"] = os.path.getsize(self.path)
        else:
            info["file tree"] = self._traverse(self.path)

        info["files"] = self.files
        return info

    def _traverse(self, path):
        """
        Build meta dictionary while walking directory.

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

            fhash = FileHash(path, self.piece_length)

            if fsize >= self.piece_length:
                self.piece_layers[fhash.root] = fhash.piece_layer

            self.hashes.append(fhash)
            self.pieces.extend(fhash.pieces)

            if fhash.padding_file:
                self.files.append(fhash.padding_file)
                self.pieces.append(fhash.padding_piece)

            if fsize == 0:
                return {"": {"length": fsize}}

            return {"": {"length": fsize, "pieces root": fhash.root}}

        tree = {}
        if os.path.isdir(path):

            for base, full in sortfiles(path):
                tree[base] = self._traverse(full)

        return tree

    def write(self, outfile=None):
        """
        Create a Hybrid metainfo dictionary.

        Args:
            outfile(`str` or `path-like`): where to write file to.
        """
        if outfile:
            pyben.dump(self.meta, outfile)

        elif self.outfile:
            outfile = self.outfile
            pyben.dump(self.meta, self.outfile)

        else:
            outfile = self.path + ".torrent"
            pyben.dump(self.meta, outfile)
        return (outfile, self.meta)


def merkle_root(blocks):
    """Calculate the merkle root for a seq of sha256 hash digests."""
    while len(blocks) > 1:
        blocks = [sha256(l + r).digest() for l, r in zip(*[iter(blocks)] * 2)]
    return blocks[0]


class FileHash:
    """
    Calculate hashes for Hybrid torrentfile.

    Args:
        path(`str` or pathlike): path to target file.
        piece_length(`int`): piece length for data chunks.
    """

    def __init__(self, path, piece_length):
        """
        Construct Hasher class instances for each file in torrent.

        Calculates sha1 and sha256 hashes for each version   # nosec
        of the Bittorrent protocols meta files.

        Args:
            path (`str`): Path to target file.
            piece_length (`int`): Meta file piece length.
        """
        self.path = path
        self.piece_length = piece_length
        self.pieces = []
        self.layer_hashes = []
        self.padding_piece = None
        self.padding_file = None
        self.num_blocks = piece_length // BLOCK_SIZE
        with open(path, "rb") as data:
            self._process_file(data)

    def _pad_remaining(self, total, blocklen):
        """
        Generate Hash sized, 0 filled bytes for padding.

        Args:
            total(`int`): length of bytes processed.
            blocklen(`int`): number of blocks processed.

        Returns:
            `int`: Padding to fill remaining portion of tree.
        """
        if not self.layer_hashes:
            next_pow_2 = 1 << int(math.log2(total) + 1)
            remaining = ((next_pow_2 - total) // BLOCK_SIZE) + 1
            return [bytes(HASH_SIZE) for _ in range(remaining)]

        return [bytes(HASH_SIZE) for _ in range(self.num_blocks - blocklen)]

    def _process_file(self, data):
        """
        Calculate layer hashes for contents of file.

        Args:
            data(`IOBufferReader`): file opened in read mode.
        """
        while True:
            plength = self.piece_length
            blocks = []
            piece = sha1()  # nosec
            total = 0
            block = bytearray(BLOCK_SIZE)
            for _ in range(self.num_blocks):
                size = data.readinto(block)
                if not size:
                    break
                total += size
                plength -= size
                blocks.append(sha256(block[:size]).digest())
                piece.update(block[:size])
            if not blocks:
                break
            if len(blocks) != self.num_blocks:
                padding = self._pad_remaining(len(blocks), size)
                blocks.extend(padding)
            self.layer_hashes.append(merkle_root(blocks))
            self.pieces.append(piece.digest())
            if plength > 0:
                self.padding_file = {
                    "attr": "p",
                    "length": size,
                    "path": [".pad", str(plength)],
                }
                self.padding_piece = sha1(bytes(plength)).digest()  # nosec
        self.calculate_root()

    def calculate_root(self):
        """Calculate the root hash for opened file."""
        self.piece_layer = b"".join(self.layer_hashes)
        if len(self.layer_hashes) > 1:
            pad_piece = merkle_root([bytes(32) for _ in range(self.num_blocks)])
            next_pow_two = 1 << (len(self.layer_hashes) - 1).bit_length()
            remainder = next_pow_two - len(self.layer_hashes)
            self.layer_hashes += [pad_piece for _ in range(remainder)]
        self.root = merkle_root(self.layer_hashes)
