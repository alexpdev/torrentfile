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
import sys
import hashlib
import datetime
from pathlib import Path
from torrentfile.bencode import Benencoder
from torrentfile.piecelength import get_piece_length

KIB = 2**10
MIB = KIB**2
GIB = KIB**3
MIN_BLOCK = 2**14

class InvalidDataType(Exception):
    pass

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

def get_pieces(paths,piece_size):
    def hash_file(path, piece_length):
        pieces = []
        with open(path,"rb") as fd:
            data = bytearray(piece_length)
            while True:
                length = fd.readinto(data)
                if length == piece_length:
                    pieces.append(sha1(data))
                elif length > 0:
                    pieces.append(sha1(data[:length]))
                else:
                    break
        return bytes().join(pieces)
    piece_layers = []
    for path in paths:
        piece = hash_file(path,piece_size)
        piece_layers.append(piece)
    return bytes().join(piece_layers)

def walk_path(base,files,all_files):
    for item in all_files:
        if os.path.isfile(item):
            desc = {b'length' :os.path.getsize(item),
                    b'path': os.path.relpath(item, base).split(os.sep)}
            files.append(desc)
    return

def folder_info(path,piece_size):
    pass



class TorrentFile:
    def __init__(self,path=None,piece_length=None,creator=None,announce=None,private=None,source=None,length=None):
        self._path = path
        self.Path = Path(path)
        self._is_file = self.Path.is_file()
        self._name = self.Path.name
        self._piece_length = piece_length
        self._creator = creator
        self._announce = announce
        self._private = private
        self._source = source
        self._length = length
        self._pieces = bytearray()
        self._files = []
        self.info = {}
        self.meta = {}

    def _get_filenames(self, directory, all_files):
        names = os.listdir(directory)
        names.sort(key=str.lower)
        for name in names:
            path = os.path.join(directory,name)
            if os.path.isfile(path):
                all_files.append(path)
            elif os.path.isdir(path):
                self._get_filenames(path, all_files)
        return all_files

    def assemble(self):
        if not self._length:
            self._length = self._path_size()
        if not self._piece_length:
            self._piece_length = get_piece_length(self._length)
        directory = os.path.abspath(self._path)
        all_files = self._get_filenames(directory, [])
        self.info[b"piece length"] = self._piece_length
        self.info["name"] = self._name.encode('utf-8')
        if self._private:
            self.info["private"] = 1 if self._private else 0
        if self._creator:
            self.info["created by"] = self._creator.encode("utf-8")
        else:
            self.info["created by"] = "pytorrentfile".encode("utf-8")
        if self._source:
            self.info["source"] = self._source.encode('utf-8')
        self.info["creation date"] = datetime.datetime.isoformat(datetime.datetime.today()).encode('utf-8')
        if self._is_file:
            self.info[b'length'] = self._length
            return self.info
        walk_path(self._name, self._files, all_files)
        self.info[b"files"] = self._files
        self.info[b'pieces'] = get_pieces(all_files,self._piece_length)
        return self.info

    def _folder_size(self,path):
        size = 0
        if path.is_file():
            size += os.path.getsize(path)
            return size
        elif path.is_dir():
            for item in path.iterdir():
                size += self._folder_size(item)
        return size

    def _path_size(self):
        if self.Path.is_file():
            return os.path.getsize(self.Path)
        return self._folder_size(self.Path)
