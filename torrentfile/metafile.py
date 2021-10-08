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
"""Creating and verfying Bittorrent v1 metafiles (.torrent)."""

import os
import math
import re
from hashlib import sha1
from datetime import datetime

from .utils import Bendecoder, Benencoder, path_stat


class TorrentFile:
    """
    Class for creating Bittorrent meta files.

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

    Returns:
        `obj`: Instance of Metafile Class.
    """

    def __init__(self, path=None, announce=None, announce_list=None,
                 private=False, source=None, piece_length=None, comment=None,
                 outfile=None):
        """
        Class for creating Bittorrent meta files.

        Construct *Torrentfile* class instance object.

        Args:
          flags('obj'): has all the following properties.

        Returns:
          `Torrentfile`: Instance of Metafile Class.
        """
        # fs path attributes.
        self.path = path
        self.name = os.path.basename(path)
        self.outfile = outfile

        # if `piece_length` is a `str` turn it into an `int`.
        if piece_length:
            self.piece_length = int(piece_length)
        else:
            self.piece_length = None
        self.announce = announce

        # If announce `list` is a `str` split it up.
        if isinstance(announce_list, str):
            self.announce_list = re.split(r"[\s,]", announce_list)
        else:
            self.announce_list = announce_list

        # for private trackers.
        self.private = private
        self.source = source

        # other less common flags.
        self.comment = comment
        self.meta = {}

    def _assemble_infodict(self):
        """Create info dictionary."""
        filelist, size, piece_length = path_stat(self.path)

        # set name of torrentfile
        info = {"name": self.name}
        # If a comment was provided place in Info dictionary.
        if self.comment:
            info["comment"] = self.comment

        # create announce list for additional trackers.
        if self.announce_list:
            info["announce list"] = self.announce_list

        # if single file, add 'length' key otherwise
        if os.path.isfile(self.path):
            info["length"] = size
        else:
            info["files"] = [
                {
                    "length": os.path.getsize(p),
                    "path": os.path.relpath(p, self.path).split(os.sep),
                }
                for p in filelist
            ]

        # set torrent piecelength.
        if self.piece_length:
            info["piece length"] = self.piece_length
        else:
            self.piece_length = info["piece length"] = piece_length

        # apply chuncks of hashed data to pieces key.
        pieces = bytearray()
        for piece in Feeder(filelist, self.piece_length, size):
            pieces.extend(piece)
        info["pieces"] = pieces

        if self.private:
            info["private"] = 1
        if self.source:
            info["source"] = self.source

        return info

    def assemble(self):
        """
        Assemble components of torrent metafile.

        Returns:
          `dict`: metadata dictionary for torrent file
        """
        if self.announce:
            self.meta["announce"] = self.announce
        else:
            self.meta["announce"] = ""

        self.meta["created by"] = "torrentfile"
        self.meta["creation date"] = int(datetime.timestamp(datetime.now()))
        self.meta["info"] = self._assemble_infodict()
        return self.meta

    def write(self, outfile=None):
        """
        Write assembled data to .torrent file.

        Args:
          outfile: (Default value = None)

        Returns:
          `tuple`: Path to output file, Pre-encoded metadata.
        """
        encoder = Benencoder()
        data = encoder.encode(self.meta)
        if outfile:
            self.outfile = outfile

        elif not self.outfile:
            self.outfile = self.meta["info"]["name"] + ".torrent"

        with open(self.outfile, "wb") as fd:
            fd.write(data)

        return (self.outfile, self.meta)


class Checker:
    """
    Check a given file or directory to see if it matches a torrentfile.

    Public constructor for Checker class instance.

    Args:
      metafile:(`str`): Path to ".torrent" file.
      location(`str`): Path where the content is located in filesystem.

    Example:
        >> metafile = "/path/to/torrentfile/content_file_or_dir.torrent"
        >> location = "/path/to/location"
        >> os.path.exists("/path/to/location/content_file_or_dir")
        Out: True
        >> checker = Checker(metafile, location)
    """

    def __init__(self, metafile, location):
        """
        Check a given file or directory to see if it matches a torrentfile.

        Public constructor for Checker class instance.

        Args:
          metafile:(`str`): Path to ".torrent" file.
          location(`str`): Path where the content is located in filesystem.
        """
        self.metafile = metafile
        self.location = location
        self.meta = {}
        self.info = {}
        self.total = 0
        self.piece_length = None
        self.files = None
        self.name = None
        self.paths = []
        self.fileinfo = {}
        self.status = 0

    def decode_metafile(self):
        """Decode bencoded data inside .torrent file."""
        fd = open(self.metafile, "rb").read()
        decoder = Bendecoder()
        terms = decoder.decode(fd)
        for key, val in terms.items():
            self.meta[key] = val
            if key == "info":
                for key1, val1 in val.items():
                    self.info[key1] = val1

        self.piece_length = self.info["piece length"]
        self.pieces = self.info["pieces"]
        self.name = self.info["name"]

        if "length" not in self.info:
            self.files = self.info["files"]

    def get_paths(self):
        """Get list of paths from files list inside .torrent file."""
        if not self.files:
            self.paths.append(self.name)
            self.fileinfo[self.name] = self.info["length"]

        else:
            for item in self.files:
                size = item["length"]
                self.total += size
                path = os.path.join(*item["path"])
                self.paths.append(path)
                self.fileinfo[path] = size
        return self.paths

    def _check_path(self, paths):
        """
        Check if paths exist.

        Args:
          paths(`list`): Paths to torrent files contents.

        Returns:
          `str`: "Complete" after finishing.
        """
        feeder = Feeder(paths, self.piece_length, self.total)
        pieces = bytes.fromhex(self.pieces)
        total = len(pieces) // 20
        counter = 0

        for digest in feeder:
            if pieces[: len(digest)] == digest:
                pieces = pieces[len(digest):]
                counter += 1

        return str(int(counter / total) * 100) + "%"

    def check_path(self):
        """
        Check if path exists and is the correct size and hash.

        Returns:
            `str`: Indicating process has completed.
        """
        if os.path.isfile(self.location):
            if os.path.basename(self.location) == self.name:
                paths = [self.location]

        else:
            paths = [os.path.join(self.location, i) for i in self.paths]

        return self._check_path(paths)

    def check(self):
        """Check if all components work as expected."""
        self.decode_metafile()

        self.get_paths()

        status = self.check_path()
        return status


class Feeder:
    """
    Construct the Feeder class.

    Seemlesly generate hashes of piece length data from filelist contents.

    Args:
      paths(`list`): List of files.
      piece_length(`int`): Size of chuncks to split the data into.
      total(`int`): Sum of all files in file list.
    """

    def __init__(self, paths, piece_length, total):
        """
        Construct the Feeder class.

        Generate hashes of piece length data from filelist contents.

        Args:
          paths(`list`): List of files.
          piece_length(`int`): Size of chuncks to split the data into.
          total(`int`): Sum of all files in file list.
        """
        self.piece_length = piece_length
        self.paths = paths
        self.total = total
        self.pieces = []
        self.index = 0
        self.current = open(self.paths[self.index], "rb")
        self.iterator = self.leaves()

    def __iter__(self):
        """
        Iterate through feed pieces.

        Returns:
          `iter(self)`: Iterator for leaves/hash pieces.
        """
        self.iterator = self.leaves()
        return self.iterator

    def __next__(self):
        """
        Return the next element from iterator.

        Returns:
          `bytes`: Piece_length length pieces of data.
        """
        return self.iterator.__next__()

    def total_pieces(self):
        """Total size / piece length."""
        return math.ceil(self.total // self.piece_length)

    def handle_partial(self, arr, partial):
        """
        Seemlessly move to next file for input data.

        Args:
          arr(`bytearray`): Incomplete piece containing partial data
          partial(`int`): Size of incomplete piece_length

        Returns:
          `bytes`: SHA1 digest of the complete piece.
        """
        while partial < self.piece_length:
            temp = bytearray(self.piece_length - partial)
            size = self.current.readinto(temp)
            arr[partial: partial + size] = temp[:size]
            partial += size
            if partial < self.piece_length:
                if not self.next_file():
                    return sha1(arr[:partial]).digest()
        return sha1(arr).digest()

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
                    self.current.close()
                    break
            elif size < self.piece_length:
                yield self.handle_partial(piece, size)
            else:
                yield sha1(piece).digest()

"""
Notes:
-------------------------------------------------------
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
