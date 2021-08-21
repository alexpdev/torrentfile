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
metainfo files
Metainfo files (also known as .torrent files) are bencoded dictionaries with the following keys:

"announce": The URL of the tracker.

"info": This maps to a dictionary, with keys described below.

"piece layers": A dictionary of strings. For each file in the file tree that is larger than the piece size it contains one string value.
> The keys are the merkle roots while the values consist of concatenated hashes of one layer within that merkle tree.
> The layer is chosen so that one hash covers piece length bytes.
> For example if the piece size is 16KiB then the leaf hashes are used.
> If a piece size of 128KiB is used then 3rd layer up from the leaf hashes is used.
> Layer hashes which exclusively cover data beyond the end of file, i.e. are only needed to balance the tree, are omitted.
> All hashes are stored in their binary format.
> A torrent is not valid if this field is absent, the contained hashes do not match the merkle roots or are not from the correct layer.

All strings in a .torrent file defined by this BEP that contain human-readable text are UTF-8 encoded.

"info" dictionary:
    "name": A display name for the torrent. It is purely advisory.

    "piece length":  The number of bytes that each logical piece in the peer protocol refers to. I.e. it sets the granularity of piece, request, bitfield and have messages. It must be a power of two and at least 16KiB.
    Files are mapped into this piece address space so that each non-empty file is aligned to a piece boundary and occurs in the same order as in the file tree. The last piece of each file may be shorter than the specified piece length, resulting in an alignment gap.

    "meta version": An integer value, set to 2 to indicate compatibility with the current revision of this specification. Version 1 is not assigned to avoid confusion with BEP3. Future revisions will only increment this value to indicate an incompatible change has been made, for example that hash algorithms were changed due to newly discovered vulnerabilities. Implementations must check this field first and indicate that a torrent is of a newer version than they can handle before performing other validations which may result in more general messages about invalid files.

    "file tree": A tree of dictionaries where dictionary keys represent UTF-8 encoded path elements. Entries with zero-length keys describe the properties of the composed path at that point. 'UTF-8 encoded' in this context only means that if the native encoding is known at creation time it must be converted to UTF-8. Keys may contain invalid UTF-8 sequences or characters and names that are reserved on specific filesystems. Implementations must be prepared to sanitize them. On most platforms path components exactly matching '.' and '..' must be sanitized since they could lead to directory traversal attacks and conflicting path descriptions. On platforms that require valid UTF-8 path components this sanitizing step must happen after normalizing overlong UTF-8 encodings.
    The file tree root dictionary itself must not be a file, i.e. it must not contain a zero-length key with a dictionary containing a length key.

File tree layout Example:
```python
{
  info: {
    file tree: {
      dir1: {
        dir2: {
          fileA.txt: {
            "": {
              length: <length of file in bytes (integer)>,
              pieces root: <optional, merkle tree root (string)>,
              ...
            }
          },
          fileB.txt: {
            "": {
              ...
            }
          }
        },
        dir3: {
          ...
        }
      }
    }
  }
}
```

Bencoded for fileA only:
`d4:infod9:file treed4:dir1d4:dir2d9:fileA.txtd0:d5:lengthi1024e11:pieces root32:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaeeeeeee`

"length": Length of the file in bytes. Presence of this field indicates that the dictionary describes a file, not a directory. Which means it must not have any sibling entries.

"pieces root": For non-empty files this is the the root hash of a merkle tree with a branching factor of 2, constructed from 16KiB blocks of the file. The last block may be shorter than 16KiB. The remaining leaf hashes beyond the end of the file required to construct upper layers of the merkle tree are set to zero. As of meta version 2 SHA2-256 is used as digest function for the merkle tree. The hash is stored in its binary form, not as human-readable string.
Note that identical files always result in the same root hash.

Interpreting paths:
`"file tree": {name.ext: {"": {length: ...}}}`
> a single-file torrent

`"file tree": {nameA.ext: {"": {length: ...}}, nameB.ext: {"": {length: ...}}, dir: {...}}`
> a rootless multifile torrent, i.e. a list of files and directories without a named common directory containing them. implementations may offer users to optionally prepend the torrent name as root to avoid file name collisions.

`"file tree": {dir: {nameA.ext: {"": {length: ...}}, nameB.ext: {"": {length: ...}}}}`
> multiple files rooted in a single directory

"infohash": The infohash is calculated by applying a hash function to the bencoded form of the info dictionary, which is a substring of the metainfo file. For meta version 2 SHA2-256 is used.
The info-hash must be the hash of the encoded form as found in the .torrent file, which is identical to bdecoding the metainfo file, extracting the info dictionary and encoding it if and only if the bdecoder fully validated the input (e.g. key ordering, absence of leading zeros). Conversely that means implementations must either reject invalid metainfo files or extract the substring directly. They must not perform a decode-encode roundtrip on invalid data.

For some uses as torrent identifier it is truncated to 20 bytes.
When verifying an infohash implementations must also check that the piece layers hashes outside the info dictionary match the pieces root fields.
"""

import os
import math
from datetime import datetime, date
from hashlib import sha256

BLOCK_SIZE = 2**14 # 16KB

class TorrentFilev2:

    def __init__(self, path, piece_length=None, private=False, source=None, announce=None, comment=None):
        self.path = path
        self.comment = comment
        self.piece_length = piece_length
        self.private = private
        self.source = source
        self.creation_date = datetime.timestamp(date.today())
        self.created_by = "ASPDEV"
        self.length = None
        self.announce = announce
        self.infohash = None
        self.piece_layers = {}
        self.file_tree = {}
        self.info = {}
        self.meta = {}

    def assemble(self):
        self.get_info()
        self.meta["piece layers"] = self.piece_layers
        if isinstance(self.announce,str):
            self.meta["announce"] = self.announce
        else:
            self.meta["announce"] = self.announce[0]
            self.info["announce list"] = self.announce[1:]
        self.meta["info"] = self.info
        if self.private:
            self.info["private"] = 1
        if self.source:
            self.info["source"] = self.source
        self.info["name"] = os.path.basepath(self.path)
        self.info["piece length"] = self.piece_length
        self.info["file tree"] = self.file_tree
        if self.length is not None:
            self.info["length"] = self.length
        self.info["meta version"] = "2"
        self.info["infohash"] = self.infohash
        self.meta["creation date"] = self.creation_date
        self.info["created by"] = self.created_by

    def process_file(self,path):
        hashes = V2Hasher(path,self.piece_length)
        self.hasher = hashes
        self.piece_layers.append(hashes)
        name = os.path.relpath(path,self.path).split(os.seq)
        self.files.append({'length': hashes.length, 'path':name})
        if hashes.length == 0:
            return {'':{'length':hashes.length}}
        else:
            return {'':{'length':hashes.length,'pieces root': hashes.root}}

    def _traverse(self, path):
        if os.path.isfile(path):
            return self.process_file(path)
        elif os.path.isdir(path):
            fds = [(p.name, p.path) for p in os.scandir(path)]
            fds.sort()
            return {p[0]: self._traverse(p[1]) for p in fds}

    def get_info(self):
        if os.path.isfile(self.path):
            self.length = os.path.getsize(self.path)
            self.file_tree = {os.path.basename(self.path):self._traverse(self.path)}
        else:
            self.file_tree = self._traverse(self.path)
        self.pieces = bytes([byte for piece in self.pieces for byte in piece])


class V2Hasher:
    def __init__(self, path, piece_length):
        self.fsize = os.path.getsize(path)
        self.piece_length = piece_length
        self.total_pieces = self.fsize / piece_length
        self.perpiece = piece_length // BLOCK_SIZE
        self.path = path
        self.length = 0
        self.pieces = []
        self.grab(path)

    def grab(self,path):
        with open(path,"rb") as fd:
            while True:
                chunk = bytearray(BLOCK_SIZE)
                blocks = []
                for i in range(self.perpiece):
                    size = fd.readinto(chunk)
                    if size == 0:
                        break
                    blocks.append(sha256(chunk[:size]).digest())
                    self.length += size
                if not len(blocks):
                    break
                if len(blocks) != self.perpiece:
                    needed = self.perpiece
                    if not len(self.pieces):
                        needed = int(math.log2(len(blocks)-1)) + 1
                    for i in range(abs(needed - len(blocks))):
                        blocks.append(bytearray(32))
                merkle_root = self.get_merkle_hash(blocks)
                self.pieces.append(merkle_root)
            self._calculate_root()

    def _calculate_root(self):
        layer_hash = self.pieces
        if len(self.pieces) > 1:
            self.pieces = b''.join(self.pieces)
            padding = self.get_merkle_hash([bytearray(32)] for _ in range(self.perpiece))
            layer_hash += [padding for _ in range(int(math.log2(len(layer_hash)-1)) + 1 - len(layer_hash))]
        self.root = self.get_merkle_hash(layer_hash)

    @staticmethod
    def get_merkle_hash(blocks):
        while len(blocks) > 1:
            blocks = [sha256(x + y).digest() for x, y in zip(*[iter(blocks)]*2)]
        return blocks[0]
