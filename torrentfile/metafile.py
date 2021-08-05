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
import hashlib
import collections
from pathlib import Path
from torrentfile.bencode import Benencoder
from torrentfile.hasher import PieceHasher

KIB = 2**10
MIB = KIB**2
MIN_BLOCK = 2**14

class InvalidDataType(Exception):
    pass

class MissingTracker(Exception):
    pass

class ODict(collections.OrderedDict):
    def __init__(self,items):
        super().__init__(items)


def sha1(data):
    piece = hashlib.sha1()
    piece.update(data)
    return piece.digest()

def sha256(data):
    piece = hashlib.sha256()
    piece.update(data)
    return piece.digest()

def md5(data):
    piece = hashlib.md5()
    piece.update(data)
    return piece.digest()

class TorrentFile:
    def __init__(self,
                path=None,
                piece_length=None,
                created_by=None,
                announce=None,
                private=None,
                source=None,
                length=None,
                comment=None,
                announce_list=None):

        self._path = path
        self.Path = Path(path)
        self._is_file = self.Path.is_file()
        self._piece_length = piece_length
        self._created_by = created_by
        self._announce = announce
        self._private = private
        self._source = source
        self._length = length
        self._comment = comment
        self._announce_list = announce_list
        self._files = []
        self.info = {}
        self.meta = {}

    def _assemble_infodict(self):
        hasher = PieceHasher(self._path, piece_length=self._piece_length)
        if self._is_file:
            self.info["length"] = hasher.length
        else:
            self.info["files"] = hasher.files
            print(self.info)
        self.info['pieces'] = hasher.get_pieces()
        self.info['piece length'] = hasher.piece_length
        self.info["name"] = os.path.split(self._path)[-1]
        if self._announce_list:
            self.info["announce-list"] = self.announce_list
        if self._source:
            self.info["source"] = self._source
        if self._comment:
            self.info["comment"] = self._comment
        if self._private:
            self.info["private"] = self._private
        return self.info

    def assemble(self):
        if not self._announce:
            raise MissingTracker
        self.meta["announce"] = self._announce
        self.meta["creation date"] = int(time.time())
        if self._created_by:
            self.meta["created by"] = self._created_by
        else:
            self.meta["created by"] = "alexpdev"
        self.meta["info"] = self._assemble_infodict()
        print(self.meta)
        encoder = Benencoder()
        data = encoder.encode(self.meta)
        self.data = data

    def write(self,outfile=None):
        if not outfile:
            outfile = self.info["name"] + ".torrent"
        with open(outfile, "wb") as fd:
            fd.write(self.data)
        print("success")
        return self.data
