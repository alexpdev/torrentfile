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
"""Piece/File Hashers for Bittorrent meta file contents."""

import logging
import os
from hashlib import sha1, sha256  # nosec

from torrentfile.utils import humanize_bytes, next_power_2

BLOCK_SIZE = 2 ** 14  # 16KiB
HASH_SIZE = 32

logger = logging.getLogger(__name__)


class CbMixin:
    """Mixin class to set a callback during hashing procedure."""

    _cb = None

    @classmethod
    def set_callback(cls, func):
        """
        Assign a callback to the Hashing class.

        Parameters
        ----------
        func : function
            the callback function
        """
        cls._cb = func


class Hasher(CbMixin):
    """Piece hasher for Bittorrent V1 files.

    Takes a sorted list of all file paths, calculates sha1 hash
    for fixed size pieces of file data from each file
    seemlessly until the last piece which may be smaller than others.

    Parameters
    ----------
    paths : `list`
        List of files.
    piece_length : `int`
        Size of chuncks to split the data into.
    total : `int`
        Sum of all files in file list.
    """

    def __init__(self, paths, piece_length):
        """Generate hashes of piece length data from filelist contents."""
        self.piece_length = piece_length
        self.paths = paths
        self.total = sum([os.path.getsize(i) for i in self.paths])
        self.index = 0
        self.current = open(self.paths[0], "rb")
        logger.debug(
            "Hashing v1 torrent file. Size: %s Piece Length: %s",
            humanize_bytes(self.total),
            humanize_bytes(self.piece_length),
        )

    def __iter__(self):
        """Iterate through feed pieces.

        Returns
        -------
        self : `iterator`
            Iterator for leaves/hash pieces.
        """
        return self

    def _handle_partial(self, arr):
        """Define the handling partial pieces that span 2 or more files.

        Parameters
        ----------
        arr : `bytearray`
            Incomplete piece containing partial data
        partial : `int`
            Size of incomplete piece_length

        Returns
        -------
        digest : `bytes`
            SHA1 digest of the complete piece.
        """
        while len(arr) < self.piece_length and self.next_file():
            target = self.piece_length - len(arr)
            temp = bytearray(target)
            size = self.current.readinto(temp)
            arr.extend(temp[:size])
            if size == target:
                break
        return sha1(arr).digest()  # nosec

    def next_file(self):
        """Seemlessly transition to next file in file list."""
        self.index += 1
        if self.index < len(self.paths):
            self.current.close()
            self.current = open(self.paths[self.index], "rb")
            return True
        return False

    def __next__(self):
        """Generate piece-length pieces of data from input file list."""
        while True:
            piece = bytearray(self.piece_length)
            size = self.current.readinto(piece)
            if size == 0:
                if not self.next_file():
                    raise StopIteration
            elif size < self.piece_length:
                return self._handle_partial(piece[:size])
            else:
                return sha1(piece).digest()  # nosec


def merkle_root(blocks):
    """Calculate the merkle root for a seq of sha256 hash digests."""
    while len(blocks) > 1:
        blocks = [sha256(x + y).digest() for x, y in zip(*[iter(blocks)] * 2)]
    return blocks[0]


class HasherV2(CbMixin):
    """Calculate the root hash and piece layers for file contents.

    Iterates over 16KiB blocks of data from given file, hashes the data,
    then creates a hash tree from the individual block hashes until size of
    hashed data equals the piece-length.  Then continues the hash tree until
    root hash is calculated.

    Parameters
    ----------
    path : `str`
        Path to file.
    piece_length : `int`
        Size of layer hashes pieces.
    """

    def __init__(self, path, piece_length):
        """Calculate and store hash information for specific file."""
        self.path = path
        self.root = None
        self.piece_layer = None
        self.layer_hashes = []
        self.piece_length = piece_length
        self.num_blocks = piece_length // BLOCK_SIZE
        logger.debug(
            "Hashing partial v2 torrent file. Piece Length: %s Path: %s",
            humanize_bytes(self.piece_length),
            str(self.path),
        )

        with open(self.path, "rb") as fd:
            self.process_file(fd)

    def process_file(self, fd):
        """Calculate hashes over 16KiB chuncks of file content.

        Parameters
        ----------
        fd : `str`
            Opened file in read mode.
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
                # when size of file doesn't fill the last block
                # when the file contains multiple pieces
                remaining = self.num_blocks - len(blocks)
                if not self.layer_hashes:
                    # when the there is only one block for file
                    power2 = next_power_2(len(blocks))
                    remaining = power2 - len(blocks)

                # pad the the rest with zeroes to fill remaining space.
                padding = [bytes(32) for _ in range(remaining)]
                blocks.extend(padding)
            # calculate the root hash for the merkle tree up to piece-length

            layer_hash = merkle_root(blocks)
            if self._cb:
                self._cb(layer_hash)
            self.layer_hashes.append(layer_hash)
        self._calculate_root()

    def _calculate_root(self):
        """Calculate root hash for the target file."""
        self.piece_layer = b"".join(self.layer_hashes)
        hashes = len(self.layer_hashes)
        if hashes > 1:
            pow2 = next_power_2(hashes)
            remainder = pow2 - hashes
            pad_piece = [bytes(HASH_SIZE) for _ in range(self.num_blocks)]
            for _ in range(remainder):
                self.layer_hashes.append(merkle_root(pad_piece))
        self.root = merkle_root(self.layer_hashes)


class HasherHybrid(CbMixin):
    """Calculate root and piece hashes for creating hybrid torrent file.

    Create merkle tree layers from sha256 hashed 16KiB blocks of contents.
    With a branching factor of 2, merge layer hashes until blocks equal
    piece_length bytes for the piece layer, and then the root hash.

    Parameters
    ----------
    path : `str`
        path to target file.
    piece_length : `int`
        piece length for data chunks.
    """

    def __init__(self, path, piece_length):
        """Construct Hasher class instances for each file in torrent."""
        self.path = path
        self.piece_length = piece_length
        self.pieces = []
        self.layer_hashes = []
        self.piece_layer = None
        self.root = None
        self.padding_piece = None
        self.padding_file = None
        self.amount = piece_length // BLOCK_SIZE
        logger.debug(
            "Hashing partial Hybrid torrent file. Piece Length: %s Path: %s",
            humanize_bytes(self.piece_length),
            str(self.path),
        )
        with open(path, "rb") as data:
            self._process_file(data)

    def _pad_remaining(self, block_count):
        """Generate Hash sized, 0 filled bytes for padding.

        Parameters
        ----------
        block_count : `int`
            current total number of blocks collected.

        Returns
        -------
        padding : `bytes`
            Padding to fill remaining portion of tree.
        """
        # when the there is only one block for file
        remaining = self.amount - block_count
        if not self.layer_hashes:
            power2 = next_power_2(block_count)
            remaining = power2 - block_count
        return [bytes(HASH_SIZE) for _ in range(remaining)]

    def _process_file(self, data):
        """Calculate layer hashes for contents of file.

        Parameters
        ----------
        data : `BytesIO`
            File opened in read mode.
        """
        while True:
            plength = self.piece_length
            blocks = []
            piece = sha1()  # nosec
            total = 0
            block = bytearray(BLOCK_SIZE)
            for _ in range(self.amount):
                size = data.readinto(block)
                if not size:
                    break
                total += size
                plength -= size
                blocks.append(sha256(block[:size]).digest())
                piece.update(block[:size])
            if not blocks:
                break
            if len(blocks) != self.amount:
                padding = self._pad_remaining(len(blocks))
                blocks.extend(padding)
            layer_hash = merkle_root(blocks)
            if self._cb:
                self._cb(layer_hash)
            self.layer_hashes.append(layer_hash)
            if plength > 0:
                self.padding_file = {
                    "attr": "p",
                    "length": size,
                    "path": [".pad", str(plength)],
                }
                piece.update(bytes(plength))
            self.pieces.append(piece.digest())  # nosec
        self._calculate_root()

    def _calculate_root(self):
        """Calculate the root hash for opened file."""
        self.piece_layer = b"".join(self.layer_hashes)

        if len(self.layer_hashes) > 1:
            pad_piece = merkle_root([bytes(32) for _ in range(self.amount)])

            pow2 = next_power_2(len(self.layer_hashes))
            remainder = pow2 - len(self.layer_hashes)

            self.layer_hashes += [pad_piece for _ in range(remainder)]
        self.root = merkle_root(self.layer_hashes)
