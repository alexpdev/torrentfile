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

import hashlib
import math
import os
from datetime import datetime

from torrentfile.exceptions import MissingPathError
from torrentfile.utils import Benencoder, path_piece_length, sortfiles

BLOCK_SIZE = 2 ** 14  # 16KB

timestamp = lambda: int(datetime.timestamp(datetime.now()))


class TorrentFileV2:
    def __init__(
        self,
        path=None,
        announce=None,
        piece_length=None,
        private=False,
        source=None,
        comment=None,
        outfile=None,
        created_by=None,
    ):
        if not path:
            raise MissingPathError
        self.name = os.path.basename(path)
        self.path = path
        self.comment = comment
        self.piece_length = piece_length
        self.private = private
        self.source = source
        self.announce = announce
        self.outfile = outfile
        self.created_by = created_by
        self.length = None
        self.hashes = []
        self.piece_layers = {}
        self.file_tree = {}
        self.info = {}
        self.meta = {}

    def _assemble_infodict(self):
        """Create info dictionary for metafile v2.

        Returns:

            * dict: info dictionary.
        """
        if self.comment: self.info["comment"] = self.comment

        if os.path.isfile(self.path):
            self.info["length"] = os.path.getsize(self.path)

        self.info["file tree"] = self.traverse(self.path)

        # Bittorrent Protocol v2
        self.info["meta version"] = 2
        # ---------------------------------------------
        self.info["name"] = self.name

        # calculate best piece length if not provided by user
        self.info["piece length"] = self.piece_length
        if self.private: self.info["private"] = 1
        if self.source: self.info["source"] = self.source

    def assemble(self):
        """*assemble* Assemble components of torrent metafile v2.

        Returns:

            * `dict`: metadata dictionary for torrent file
        """

        # if no tracker url was provided, place dummy string in its place
        # which can be later replaced by some Bittorrent clients
        if not self.announce:
            self.meta["announce"] = "UnkownTrackerGoesHere"

        elif isinstance(self.announce, str):
            self.meta["announce"] = self.announce
        else:
            # if announce is iterable, only first url is used
            self.meta["announce"] = self.announce[0]

        if not self.piece_length:
            self.piece_length = path_piece_length(self.path)

        self.meta["created by"] = "torrentfile"
        self.meta["creation date"] = timestamp()

        # assemble info dictionary and assign it to info key in meta
        self._assemble_infodict()

        for hasher in self.hashes:
            if hasher.piece_layers:
                self.piece_layers[hasher.root_hash] = hasher.piece_layers

        self.meta["info"] = self.info
        self.meta["piece layers"] = self.piece_layers

        encoder = Benencoder()
        self.data = encoder.encode(self.meta)

    def traverse(self, path):
        if os.path.isfile(path):
            size = os.path.getsize(path)
            if size == 0:
                return {"": {"length": size}}
            else:
                hashes = FileHash(path, self.piece_length, size)
                self.hashes.append(hashes)
                return {"": {"length": size, "pieces root": hashes.root_hash}}
        elif os.path.isdir(path):
            file_tree = {}
            for base, full in sortfiles(path):
                file_tree[base] = self.traverse(full)
        return file_tree

    def write(self, outfile=None):
        """self.write(outfile)

        Write assembled data to .torrent file.

        Args
        ------------

            outfile:
                str: path to save location.

        Returns
        -----------

            bytes:
                data writtend to .torrent file.
        """
        if outfile:
            self.outfile = outfile
        elif not self.outfile:
            self.outfile = self.info["name"] + ".torrent"
        with open(self.outfile, "wb") as fd:
            fd.write(self.data)
        return self.outfile, self.meta


class FileHash:
    def __init__(self, path, piece_length, size):
        self.path = path
        self.root_hash = None
        self.piece_layers = None
        self.layer_hashes = []
        self.fsize = size
        self.piece_length = piece_length
        self.pieces_left = self.fsize // piece_length
        self.blocks_per_piece = piece_length // BLOCK_SIZE
        self.process_file()

    def process_file(self):
        with open(self.path, "rb") as fd:
            while True:
                blocks = []
                leaf = bytearray(BLOCK_SIZE)
                for _ in range(self.blocks_per_piece):
                    size = fd.readinto(leaf)
                    if not size:
                        break
                    blocks.append(sha256(leaf[:size]))
                if not len(blocks): break
                if len(blocks) < self.blocks_per_piece:
                    remaining = ((1 << (len(blocks) - 1).bit_length())
                                // BLOCK_SIZE) - len(blocks)
                    blocks += [bytes(32) for _ in range(remaining)]
                self.layer_hashes.append(merkle_root(blocks))
            self._calculate_root()

    def _calculate_root(self):
        if len(self.layer_hashes) > 1:
            self.piece_layers = b"".join(self.layer_hashes)
        self.root_hash = merkle_root(self.layer_hashes)

def merkle_root(pieces):
    while len(pieces) > 1:
        pieces = [sha256(x + y) for x, y in zip(*[iter(pieces)] * 2)]
    return pieces[0]

def sha256(data):
    _hash = hashlib.sha256(data)
    return _hash.digest()
