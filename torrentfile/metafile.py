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
Creating and verfying Bittorrent v1 metafiles (.torrent).

## Notes
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
import math
import os
from hashlib import sha1  # nosec

from .metabase import MetaFile
from .utils import filelist_total


class TorrentFile(MetaFile):
    """Class for creating Bittorrent meta files.

    Construct *Torrentfile* class instance object.

    Args:
        path(`str`): Path to torrent file or directory.
        piece_length(`int`): Size of each piece of torrent data.
        announce(`str`): Tracker URL.
        announce_list(`str` or `list`): Additional Tracker URLs.
        private(`int`): 1 if private torrent else 0.
        source(`str`): Source tracker.
        comment(`str`): Comment string.
        outfile(`str`): Path to write metfile to.
    """

    def __init__(self, **kwargs):
        """Construct TorrentFile class instance with given keyword args.

        Args:
            kwargs (`dict`): dictionary of keyword args passed to superclass.
        """
        super().__init__(**kwargs)
        logging.debug("Making .torrent v1 file.")
        self.meta = self.assemble()

    def _assemble_infodict(self):
        """Create info dictionary.

        Returns:
            info (`dict`): .torrent info dictionary.
        """
        info = {"name": os.path.basename(self.path)}

        size, filelist = filelist_total(self.path)

        if self.comment:
            info["comment"] = self.comment

        if self.announce_list:
            info["announce list"] = self.announce_list

        info["piece length"] = self.piece_length

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
        feeder = Feeder(filelist, self.piece_length, size)
        for piece in feeder:
            pieces.extend(piece)

        info["pieces"] = pieces

        if self.private:
            info["private"] = 1

        if self.source:
            info["source"] = self.source
        return info

    def assemble(self):
        """Assemble components of torrent metafile.

        Returns:
          `dict`: metadata dictionary for torrent file
        """
        meta = self.apply_constants()
        meta["info"] = self._assemble_infodict()
        return meta


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
