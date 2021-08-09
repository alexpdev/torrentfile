#! /usr/bin/python3
# -*- coding: utf-8 -*-

#####################################################################
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#####################################################################
"""
metainfo files

Metainfo files (also known as .torrent files) are bencoded dictionaries with
the following keys:

announce

```
The URL of the tracker.
```

info

```
This maps to a dictionary, with keys described below.
```

All strings in a .torrent file that contains text must be UTF-8 encoded.

## info dictionary

The `name` key maps to a UTF-8 encoded string which is the suggested name to
save the file (or directory) as. It is purely advisory.

`piece length` maps to the number of bytes in each piece the file is split
into. For the purposes of transfer, files are split into fixed-size pieces
which are all the same length except for possibly the last one which may be
truncated. `piece length` is almost always a power of two, most commonly 2 18
= 256 K (BitTorrent prior to version 3.2 uses 2 20 = 1 M as default).

`pieces` maps to a string whose length is a multiple of 20\. It is to be
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

`length` \- The length of the file, in bytes.

`path` \- A list of UTF-8 encoded strings corresponding to subdirectory names,
the last of which is the actual file name (a zero length list is an error
case).

In the single file case, the name key is the name of a file, in the muliple
file case, it's the name of a directory.
"""
import os
import time
from torrentfile.feeder import Feeder
from torrentfile.utils import path_stat, do_something, Benencoder


class MissingTracker(Exception):
    """Exception for missing torrent fields."""

    pass


class TorrentFile:
    """Class for creating Bittorrent meta files."""

    def __init__(
        self,
        path=None,
        piece_length=None,
        created_by=None,
        announce=None,
        private=None,
        source=None,
        length=None,
        comment=None,
        announce_list=None,
        v2=False,
    ):
        """Constructor for Torrentfile Class

        Args:
            path (str): path to torrent file or directory.
            piece_length (int): size of each piece of torrent data.
            created_by (str): creator.
            announce (str): tracker url.
            private (int): 1 if private torrent else 0.
            source (str): source tracker.
            length (int): size of torrent.
            comment (str): comment string.
            announce_list (list): List of tracker urls.
            v2 (bool): Torrent v2 or v1.
        """
        self.path = path
        self.name = os.path.basename(self._path)
        self.base = path
        self.piece_length = piece_length
        self.created_by = created_by
        self.announce = announce
        self.private = private
        self.source = source
        self.length = length
        self.comment = comment
        self.announce_list = announce_list
        self.v2 = v2
        self.files = []
        self.info = {}
        self.meta = {}

    def _assemble_infodict(self):
        """
        Create info dictionary.

        Returns:
            dict: info dictionary.
        """
        filelist, size, piece_length = path_stat(self.base)
        # create dictionary keys for available fields.
        if self.announce_list:
            self.info["announce-list"] = self.announce_list
        # add comment
        if self.comment:
            self.info["comment"] = self.comment
        # if single file, add 'length' key otherwise
        if os.path.isfile(self.base):
            self.info["length"] = size
        else:
            self.files = self.info["files"] = [
                {
                    "length": os.path.getsize(p),
                    "path": os.path.relpath(p, self.base).split(os.sep),
                }
                for p in filelist
            ]
        self.info["name"] = self.name
        if not self.piece_length:
            self.info["piece length"] = self.piece_length = piece_length
        else:
            self.info["piece length"] = self.piece_length
        feeder = Feeder(filelist, self.piece_length, size, sha256=False)
        pieces = bytearray()
        for piece in feeder:
            pieces.extend(piece)
        self.info["pieces"] = pieces
        if self._private:
            self.info["private"] = self._private
        if self._source:
            self.info["source"] = self._source
        return self.info

    def assemble(self):
        """
        Assemble components of torrent metafile.

        Raises:
            MissingTracker: Announce field is required for all torrents.

        Returns:
            dict: metadata dictionary for torrent file
        """
        if not self.announce:
            raise MissingTracker
        self.meta["announce"] = self.announce

        if self.created_by:
            self.meta["created by"] = self.created_by
        else:
            self.meta["created by"] = "alexpdev"

        self.meta["creation date"] = int(time.time())
        if self.v2:
            self.data = do_something()
        else:
            self.meta["info"] = self._assemble_infodict()
            encoder = Benencoder()
            self.data = encoder.encode(self.meta)
        return self.data

    def write(self, outfile=None):
        """
        Write assembled data to .torrent file.

        Args:
            outfile (str, optional): path to save location. Defaults to None.

        Returns:
            bytes: data writtend to .torrent file
        """
        if not outfile:
            outfile = self.info["name"] + ".torrent"
        with open(outfile, "wb") as fd:
            fd.write(self.data)
        print("success")
        return self.data
