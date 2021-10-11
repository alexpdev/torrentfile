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

import os
from datetime import datetime
from hashlib import sha1, sha256  # nosec

from .utils import Benencoder, path_piece_length

BLOCK_SIZE = 2 ** 14


class TorrentFileHybrid:
    """Create Bittorrent v1 v2 hybrid metafiles."""

    def __init__(self, path=None, announce=None, announce_list=None,
                 comment=None, source=None, outfile=None, private=None,
                 piece_length=None):
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
        self.path = path
        self.name = os.path.basename(path)
        self.announce = announce
        self.announce_list = announce_list
        self.comment = comment
        self.source = source
        self.private = private
        self.piece_length = piece_length
        self.outfile = outfile

        self.piece_layers = []
        self.pieces = []
        self.files = []
        self.residuals = None
        self.meta = self.assemble()

    def _assemble_infodict(self):
        """
        Assemble info dictionary contained in meta info.

        Returns:
            info(`dict`): Info dictionary.
        """
        info = {"meta version": 2}

        if not self.piece_length:
            self.piece_length = path_piece_length(self.path)
            info["piece length"] = self.piece_length
        elif isinstance(self.piece_length, str):
            info["piece length"] = self.piece_length = int(self.piece_length)

        if self.announce_list:
            info["announce list"] = self.announce_list

        if os.path.isfile(self.path):
            info["file tree"] = {self.name: self._traverse(self.path)}
            info["length"] = os.path.getsize(self.path)
        else:
            info["file tree"] = self._traverse(self.path)
        info["files"] = self.files
        return info

    def assemble(self):
        """Assemble the parts of the torrentfile into meta dictionary."""
        if not self.announce:
            meta = {"announce": ""}
        else:
            meta = {"announce": self.announce}

        meta["created by"] = "torrentfile"

        meta["creation date"] = int(datetime.timestamp(datetime.now()))

        meta["info"] = self._assemble_infodict()

        meta["pieces"] = self.pieces

        meta["piece_layers"] = self.piece_layers

        return meta

    def _traverse(self, path):
        """
        Build meta dictionary while walking directory.

        Args:
            path (`str`): Path to target file.
        """
        tree = {}
        if os.path.isfile(path):
            hashes = Hasher(path, self.piece_length)
            if hashes.size >= self.piece_length:
                self.piece_layers.append({hashes.root: hashes.hashv2})
            self.pieces.extend([hashes.hashv1])
            self.files.append(
                {
                    "length": hashes.size,
                    "path": os.path.relpath(path, self.path).split(os.sep),
                }
            )

            if hashes.size == 0:
                return {"": {"length": hashes.size}}
            return {"": {"length": hashes.size, "pieces root": hashes.root}}
        if os.path.isdir(path):
            dirlist = sorted(os.listdir(path), key=str.lower)
            for item in map(lambda x: os.path.join(path, x), dirlist):
                tree[os.path.basename(item)] = self._traverse(item)
        return tree

    def write(self, outfile=None):
        """
        Create a Hybrid metainfo dictionary.

        Args:
            outfile(`str` or `path-like`): where to write file to.
        """
        if outfile:
            self.outfile = outfile
        elif not self.outfile:
            self.outfile = os.path.basename(self.path) + ".torrent"
        encoder = Benencoder()
        data = encoder.encode(self.meta)
        with open(self.outfile, "wb") as fd:
            fd.write(data)
        return (self.outfile, self.meta)


def merkle_root(blocks):
    """Calculate the merkle root for a seq of sha256 hash digests."""
    while len(blocks) > 1:
        blocks = [sha256(l + r).digest() for l, r in zip(*[iter(blocks)] * 2)]
    return blocks[0]


class Hasher:
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
        self.size = 0
        self.hashv1 = []
        self.hashv2 = []
        self.padding_hash = None
        self.padding_file = None
        num_blocks = piece_length // BLOCK_SIZE

        with open(path, "rb") as data:
            block = bytearray(BLOCK_SIZE)
            while True:
                residue = piece_length
                v2blocks = []
                v1blocks = bytearray()

                for _ in range(num_blocks):
                    size = data.readinto(block)
                    if size == 0:
                        break
                    self.size += size
                    residue -= size
                    v2blocks.append(sha256(block[:size]).digest())
                    v1blocks.extend(block[:size])

                if len(v2blocks) == 0:
                    break

                if len(v2blocks) != num_blocks:
                    if not self.hashv2:
                        leaves = 1 << (len(v2blocks) - 1).bit_length()
                    else:
                        leaves = num_blocks

                    needed = leaves - len(v2blocks)
                    v2blocks.extend([bytes(32) for _ in range(needed)])
                    self._apply_padding(residue)

                self.hashv2.append(merkle_root(v2blocks))
                self.hashv1.append(sha1(v1blocks).digest())  # nosec

        if self.size > 0:
            layer_hashes = self.hashv2
            if len(self.hashv2) > 1:
                self.hashv2 = b"".join(self.hashv2)
                pad_piece = merkle_root([bytes(32)] * num_blocks)
                power_two = 1 << (len(layer_hashes) - 1).bit_length()
                remainder = power_two - len(layer_hashes)
                layer_hashes.extend(pad_piece for _ in range(remainder))
                self._apply_padding((BLOCK_SIZE * num_blocks) * remainder)
            self.root = merkle_root(layer_hashes)

    def _apply_padding(self, size):
        self.padding_file = {
            "attr": "p",
            "length": size,
            "path": [".pad", str(size)],
        }
        self.padding_hash = sha1(bytes(size)).digest()
