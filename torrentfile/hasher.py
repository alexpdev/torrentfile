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
import math
from hashlib import sha1, sha256  # nosec

BLOCK_SIZE = 2 ** 14  # 16KiB
HASH_SIZE = 32


class Feeder:
    """Construct the Feeder class.

    Seemlesly generate hashes of piece length data from filelist contents.

    Args:
      paths (`list`): List of files.
      piece_length (`int`): Size of chuncks to split the data into.
      total (`int`): Sum of all files in file list.
    """

    def __init__(self, paths, piece_length, total):
        """Generate hashes of piece length data from filelist contents."""
        self.piece_length = piece_length
        self.paths = paths
        self.total = total
        self.pieces = []
        self.index = 0
        self.piece_count = 0
        self.num_pieces = math.ceil(self.total // self.piece_length)
        self.current = open(self.paths[0], "rb")
        self.iterator = None

    def __iter__(self):
        """Iterate through feed pieces.

        Returns:
          self (`iterator`): Iterator for leaves/hash pieces.
        """
        self.iterator = self.leaves()
        return self.iterator

    def handle_partial(self, arr, partial):
        """Seemlessly move to next file for input data.

        Args:
          arr (`bytearray`): Incomplete piece containing partial data
          partial (`int`): Size of incomplete piece_length

        Returns:
          digest (`bytes`): SHA1 digest of the complete piece.
        """
        while partial < self.piece_length and self.next_file():
            target = self.piece_length - partial
            temp = bytearray(target)
            size = self.current.readinto(temp)
            arr.extend(temp[:size])
            partial += size
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

    def leaves(self):
        """Generate piece-length pieces of data from input file list."""
        while True:
            piece = bytearray(self.piece_length)
            size = self.current.readinto(piece)
            if size == 0:
                if not self.next_file():
                    break
            elif size < self.piece_length:
                yield self.handle_partial(piece[:size], size)
            else:
                yield sha1(piece).digest()  # nosec
            self.piece_count += 1


def merkle_root(blocks):
    """Calculate the merkle root for a seq of sha256 hash digests."""
    while len(blocks) > 1:
        blocks = [sha256(x + y).digest() for x, y in zip(*[iter(blocks)] * 2)]
    return blocks[0]


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


class HybridHash:
    """Calculate hashes for Hybrid torrentfile.

    Uses sha1 and sha256 hashes for each version  # nosec
    of the Bittorrent protocols meta files respectively.

    Args:
        path (`str`): path to target file.
        piece_length (`int`): piece length for data chunks.
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
        logging.debug("Beginning file hashing: %s", self.path)
        with open(path, "rb") as data:
            self._process_file(data)

    def _pad_remaining(self, total, blocklen):
        """Generate Hash sized, 0 filled bytes for padding.

        Args:
            total (`int`): length of bytes processed.
            blocklen (`int`): number of blocks processed.

        Returns:
            padding (`bytes`): Padding to fill remaining portion of tree.
        """
        if not self.layer_hashes:
            next_pow_2 = 1 << int(math.log2(total) + 1)
            remaining = ((next_pow_2 - total) // BLOCK_SIZE) + 1
            return [bytes(HASH_SIZE) for _ in range(remaining)]

        return [bytes(HASH_SIZE) for _ in range(self.amount - blocklen)]

    def _process_file(self, data):
        """Calculate layer hashes for contents of file.

        Args:
            data (`BytesIO`): File opened in read mode.
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
                padding = self._pad_remaining(len(blocks), size)
                blocks.extend(padding)
            layer_hash = merkle_root(blocks)
            self.layer_hashes.append(layer_hash)
            if plength > 0:
                self.padding_file = {
                    "attr": "p",
                    "length": size,
                    "path": [".pad", str(plength)],
                }
                piece.update(bytes(plength))
            self.pieces.append(piece.digest())  # nosec
        self.calculate_root()

    def calculate_root(self):
        """Calculate the root hash for opened file."""
        self.piece_layer = b"".join(self.layer_hashes)

        if len(self.layer_hashes) > 1:
            pad_piece = merkle_root([bytes(32) for _ in range(self.amount)])

            next_pow_two = 1 << (len(self.layer_hashes) - 1).bit_length()
            remainder = next_pow_two - len(self.layer_hashes)

            self.layer_hashes += [pad_piece for _ in range(remainder)]
        self.root = merkle_root(self.layer_hashes)
