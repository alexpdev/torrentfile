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
from hashlib import sha1, sha256
from .utils import path_piece_length, Benencoder

BLOCK_SIZE = 2**14

class TorrentFileHybrid:
    """Create Bittorrent v1 v2 hybrid metafiles."""

    def __init__(self, path=None, announce=None, announce_list=None,
                 comment=None, source=None, outfile=None, private=None,
                 piece_length=None):
        """
        Constructor for the Hybrid torrent meta file.

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
        self.meta = {}
        self.info = self.meta["info"] = {}
        self.name = self.info["name"] = os.path.basename(path)

        if announce:
            self.meta["announce"] = announce
        else:
            self.meta["announce"] = ""

        if announce_list:
            self.info["announce list"] = announce_list

        if comment:
            self.info["comment"] = comment

        if source:
            self.info["source"] = source

        if private:
            self.info["private"] = private

        if piece_length:
            if isinstance(piece_length, str):
                self.info["piece_length"] = int(piece_length)
            else:
                self.info["piece_length"] = piece_length
        else:
            self.info["piece_length"] = path_piece_length(self.path)
        self.piece_length = self.info["piece_length"]

        self.meta["created by"] = "torrentfile"
        self.meta["creation date"] = int(datetime.timestamp(datetime.now()))
        self.info["meta version"] = 2

        self.outfile = outfile
        self.piece_layers = []
        self.pieces = []
        self.files = []
        self.residuals = None

    def assemble(self):
        """Assemble info and meta dictionaries for torrent contents."""
        if os.path.isfile(self.path):
            self.info["file tree"] = {self.name: self.traverse(self.path)}
            self.info["length"] = os.path.getsize(self.path)
        else:
            self.info["file tree"] = self.traverse(self.path)

        if len(self.files) > 1:
            self.pieces.append(self.residuals.with_pad_file())
            self.files.append({
                'attr': 'p',
                'length': self.residuals.padding_size,
                'path': ['.pad', str(self.residuals.padding_size)]
            })
        else:
            self.pieces.append(self.residuals.without_pad_file())

        self.pieces = bytes([byte for piece in self.pieces for byte in piece])
        self.meta['pieces'] = self.pieces
        self.info['files'] = self.files
        self.meta['piece_layers'] = self.piece_layers

        return self.meta


    def traverse(self, path):
        """
        Build meta dictionary while walking directory.

        Args:
            path (`str`): Path to target file.
        """
        tree = {}
        if os.path.isfile(path):
            if self.residuals:
                self.pieces.append(self.residuals.with_pad_file())
                self.files.append({
                    'attr': 'p',
                    'length': self.residuals.padding_size,
                    'path': ['.pad', str(self.residuals.padding_size)]
                })
                self.residuals = None
            hashes = Hasher(path, self.piece_length)
            self.residuals = hashes
            if hashes.size >= self.piece_length:
                self.piece_layers.append({hashes.root: hashes.piecesv2})
            self.pieces.extend(hashes.piecesv1)
            self.files.append({
                'length': hashes.size,
                'path': os.path.relpath(path, self.path).split(os.sep)
            })
            if hashes.size == 0:
                return {'': {'length': hashes.size}}
            return {'': {
                'length': hashes.size,
                'pieces root': hashes.root
            }}
        if os.path.isdir(path):
            dirlist = sorted(os.listdir(path),key=str.lower)
            for item in map(lambda x: os.path.join(path, x), dirlist):
                tree[os.path.basename(item)] = self.traverse(item)
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
        blocks = [sha256(l + r).digest() for l, r in zip(*[iter(blocks)]*2)]
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
        Constructor for Hasher class.

        Calculates sha1 and sha256 hashes for each version
        of the Bittorrent protocols meta files.

        Args:
            path (`str`): Path to target file.
            piece_length (`int`): Meta file piece length.
        """
        self.path = path
        self.size = 0
        self.piecesv1 = []
        self.piecesv2 = []
        num_blocks = piece_length // BLOCK_SIZE

        with open(path, 'rb') as data:
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
                    leaves = (1<<(len(v2blocks)-1).bit_length()
                    ) if not self.piecesv2 else num_blocks

                    v2blocks.extend(
                        [bytes(32) for i in range(leaves - len(v2blocks))])
                self.piecesv2.append(merkle_root(v2blocks))

                if residue > 0:
                    self.padding_size = residue
                    self.padding_hash = v1blocks
                else:
                    self.piecesv1.append(sha1(v1blocks).digest())

        if self.size > 0:
            layer_hashes = self.piecesv2
            if len(self.piecesv2) > 1:
                self.piecesv2 = b"".join(self.piecesv2)
                pad_piece = merkle_root([bytes(32)] * num_blocks)
                layer_hashes.extend([pad_piece for _ in range(
                    (1<<(len(layer_hashes)-1).bit_length()) - len(layer_hashes)
                )])
            self.root = merkle_root(layer_hashes)

    def with_pad_file(self):
        """Add padding to file tree to align with piece length."""
        self.padding_hash.extend(bytes(self.padding_size))
        return sha1(self.padding_hash).digest()

    def without_pad_file(self):
        """Remove residual padding files."""
        return sha1(self.padding_hash).digest()
