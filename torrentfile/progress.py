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
"""Module container Checker classes and providing checker functionality."""

import logging
import os
from hashlib import sha1  # nosec

import pyben

from torrentfile.hybrid import HybridHash
from torrentfile.metafile2 import V2Hash

SHA1 = 20
SHA256 = 32


class FeedChecker:
    """Construct the FeederChecker.

    Seemlesly validate torrent file contents by comparing hashes in
    metafile against data on disk.

    Args:
      paths (`list`): List of stirngs indicating file paths.
      piece_length (`int`): Size of data blocks to split the data into.
      total (`int`): Sum total in bytes of all files in file list.
      fileinfo (`dict`): Info and meta dictionary from .torrent file.
    """

    def __init__(self, paths, piece_length, fileinfo, pieces):
        """Generate hashes of piece length data from filelist contents."""
        self.piece_length = piece_length
        self.paths = paths
        self.pieces = pieces
        self.fileinfo = fileinfo
        self.index = 0
        self.piece_count = 0
        self.itor = None

    def __iter__(self):
        """Assign iterator and return self."""
        self.itor = self.iter_pieces()
        return self

    def __next__(self):
        """Yield back result of comparison."""
        partial = next(self.itor)
        chunck = sha1(partial).digest()  # nosec
        piece = self.pieces[self.piece_count]
        self.piece_count += 1
        path = self.paths[self.index]
        if chunck == piece:
            return True, path, piece
        return False, path, piece

    @property
    def current_length(self):
        """Length of current file contents in bytes."""
        return self.fileinfo[self.paths[self.index]]["length"]

    def iter_pieces(self):
        """Iterate through, and hash pieces of torrent contents.

        Yields:
            piece (`bytes`): hash digest for block of torrent data.
        """
        partial = bytearray()
        for i, path in enumerate(self.paths):
            self.index = i
            if os.path.exists(path):
                for piece in self.extract(path, partial):
                    if len(piece) == self.piece_length:
                        yield piece
                        partial = bytearray()
                    else:
                        partial = piece
            else:
                for blank in self._gen_blanks(partial):
                    if len(blank) == self.piece_length:
                        yield blank
                        partial = bytearray
                    else:
                        partial = blank

    def extract(self, path, partial):
        """Split file paths contents into blocks of data for hash pieces.

        Args:
            path (`str`): path to content.
            partial (`bytes`): any remaining content from last file.

        Yields:
            partial (`bytes`): Hash digest for block of .torrent contents.
        """
        read = 0
        size = os.path.getsize(path)
        length = self.fileinfo[path]["length"]
        with open(path, "rb") as current:
            while True:
                bitlength = self.piece_length - len(partial)
                part = bytearray(bitlength)
                amount = current.readinto(part)
                read += amount
                partial.extend(part[:amount])
                if amount < bitlength:
                    if size == read == length:
                        yield partial
                    break
                yield partial
                partial = bytearray(0)

        while length - size > 0:
            left = self.piece_length - len(partial)
            if length - size > left:
                padding = bytearray(left)
                size += left
                partial.extend(padding)
                yield partial
                partial = bytearray(0)
            else:
                partial.extend(bytearray(length - size))
                size += (length - size)
                yield partial

    def _gen_blanks(self, partial):
        """Create pieces filled with 0's where file sizes do not match.

        Args:
            partial (`bytes`): any remaining data from last file processed.
        """
        left = self.current_length - len(partial)
        while left > self.piece_length - len(partial):
            arrlen = self.piece_length - len(partial)
            arr = bytearray(arrlen)
            partial.extend(arr)
            left -= arrlen
            yield partial
            partial = bytearray(0)
        partial.extend(bytearray(left))
        yield partial


class Hasher:
    """Construct the HybridChecker.

    Verify that root hashes of content files match the .torrent files.

    Args:
      paths (`list`): List of files.
      piece_length (`int`): Size of chuncks to split the data into.
      fileinfo (`dict`): Info from .torrent file being checked.
    """

    def __init__(self, paths, piece_length, fileinfo, hasher):
        """Construct a HybridChecker instance."""
        self.paths = paths
        self.hasher = hasher
        self.piece_length = piece_length
        self.fileinfo = fileinfo
        self.itor = None

    def __iter__(self):
        """Assign iterator and return self."""
        self.itor = self.iter_paths()
        return self

    def __next__(self):
        """Provide the result of comparison."""
        try:
            value = next(self.itor)
            return value
        except StopIteration as stopiter:
            raise StopIteration() from stopiter

    def iter_paths(self):
        """Iterate through and compare root file hashes to .torrent file.

        Args:
            hasher (class): The class user to caluclate root hash.

        Yields:
            results (`tuple`): The size of the file and result of match.
        """
        for path in self.paths:
            info = self.fileinfo[path]
            length = info["length"]
            if not os.path.exists(path):
                if length < self.piece_length:
                    pieces = [info["pieces root"]]
                else:
                    pieces = info["layer hashes"]
                for piece in pieces:
                    yield False, path, piece
                continue
            hashed = self.hasher(path, self.piece_length)
            if length < self.piece_length:
                hash_pieces = [hashed.root]
                info_pieces = [info["pieces root"]]
            else:
                hash_pieces = split_pieces(hashed.piece_layer, SHA256)
                info_pieces = info["layer hashes"]
            diff = len(info_pieces) - len(hash_pieces)
            if diff > 0:
                hash_pieces += [bytes(SHA256)] * diff
            for actual, expected in zip(hash_pieces, info_pieces):
                if actual == expected:
                    yield True, path, actual
                else:
                    yield False, path, expected


class CheckerClass:
    """Check a given file or directory to see if it matches a torrentfile.

    Public constructor for Checker class instance.

    Args:
      metafile (`str`): Path to ".torrent" file.
      location (`str`): Path where the content is located in filesystem.

    Example:
        >> metafile = "/path/to/torrentfile/content_file_or_dir.torrent"
        >> location = "/path/to/location"
        >> os.path.exists("/path/to/location/content_file_or_dir")
        Out: True
        >> checker = Checker(metafile, location)
    """

    hook_log = None
    hook_status = None

    def __init__(self, metafile, path):
        """Validate data against hashes contained in .torrent file.

        Args:
            metafile (`str`): path to .torrent file
            path (`str`): path to content or contents parent directory.
        """
        self.result = None
        self.root = path
        self.metafile = metafile
        self.log_msg("Checking: %s, %s", metafile, path)
        self.info = self.parse_metafile()
        self.root = self.find_root()
        if self.result != "ERROR":
            self.version = check_meta_version(self.info)
            self.log_msg("Detected Meta Version %s.", str(self.version))
            self.name = self.info["name"]
            self.piece_length = self.info["piece length"]
            self.total = 0
            self.paths = []
            self.fileinfo = {}
            self.check_paths()

    @classmethod
    def register_callbacks(cls, hook1=None, hook2=None):
        """Register hooks from 3rd party programs to access generated info.

        Args:
            hook1 (`function`): callback function for the logging feature.
            hook2 (`function`): callback function for update progress.
        """
        cls.hook_log = hook1
        cls.hook_status = hook2

    def parse_metafile(self):
        """Flatten Meta dictionary of torrent file.

        Returns:
            info (`dict`): flattened meta dictionary.
        """
        if not os.path.exists(self.metafile):
            self.result = "ERROR"
            return self.result

        info = {}
        for k, v in pyben.load(self.metafile).items():
            if k == "info":
                for key, val in v.items():
                    info[key] = val
            else:
                info[k] = v
        return info

    def log_msg(self, *args):
        """Log msg to logger and send to callback hook."""
        logging.debug(*args)
        if self.hook_log is not None:
            if len(args) == 1:
                msg = args[0]
            elif len(args) == 2:
                msg = (args[0] % args[1])
            elif len(args) >= 3:
                msg = (args[0] % tuple(args[1:]))
            if msg:
                self.hook_log(msg)

    def find_root(self):
        """Find the root file or directory for torrent file contents.

        If the path specified is not the root, then search the
        provided path for content.

        Returns:
            root (`str`): root path to content
        """
        if not os.path.exists(self.root) or self.result == "ERROR":
            self.result = "ERROR"
            return self.result
        self.root = os.path.abspath(self.root)
        base = os.path.basename(self.root)

        if base == self.info["name"]:
            self.log_msg("%s is correct torrent root.", self.root)
            return self.root

        self.log_msg("Searching for torrent root in %s", self.root)
        for name in os.listdir(self.root):
            if name == self.info["name"]:
                root = os.path.join(self.root, name)
                self.log_msg("Found root: %s", root)
                return root

        self.log_msg("Could not locate data in directory: %s", self.root)
        self.result = "ERROR"
        return self.result

    def check_paths(self):
        """Gather all file paths described in the torrent file."""
        if self.version == 1:

            #  If content is only one file
            if os.path.isfile(self.root):
                self.log_msg("Single file torrent detected.")
                self.paths.append(self.root)
                self.fileinfo[self.root] = {"length": self.info["length"]}
                self.total += self.info["length"]

            # Otherwise Content is more than 1 file.
            else:
                for path in self.info["files"]:
                    self.total += path["length"]
                    rlpath = os.path.join(*path["path"])
                    full = os.path.join(self.root, rlpath)
                    self.log_msg("Adding %s to file collection.", rlpath)
                    self.fileinfo[full] = {"length": path["length"]}
                    self.paths.append(full)

            # Split pieces into individual hash digests.
            self.pieces = split_pieces(self.info["pieces"], SHA1)
            return self.feeder()

        if os.path.isfile(self.root):
            self.log_msg("Single file torrent detected.")
            meta = self.info["file tree"][self.name][""]

            # File info will store necessary data for re-check
            fileinfo = self.fileinfo[self.root] = {
                "partial": self.name,
                "length": meta["length"],
                "pieces root": meta["pieces root"]
            }

            # gather layer hashes for file and add to fileinfo
            if meta["length"] > self.piece_length:
                layer_hashes = self.info["piece layers"][meta["pieces root"]]
                fileinfo["layer hashes"] = split_pieces(layer_hashes, SHA256)
            self.total += meta["length"]
            self.paths.append(self.root)

        else:
            self.walk_file_tree(self.info["file tree"], [])
        return self.hasher()

    def walk_file_tree(self, tree, partials):
        """Traverse File Tree dictionary.

        Extract full pathnames, length, and root hash for each file
        included in the .torrent file.

        Args:
            tree (`dict`): File Tree dict extracted from torrent file.
            partials (`list`): list of intermediate pathnames.
        """
        for key, val in tree.items():

            # Empty string means the tree's leaf is value
            if "" in val:
                path = os.path.join(self.root, *partials, key)
                self.log_msg("Adding %s to file collection.", path)
                self.paths.append(path)
                info = self.fileinfo[path] = val[""]
                size = val[""]["length"]
                self.total += size
                info["partial"] = key

                # get layer hashes for this file
                if size > self.piece_length:
                    root = val[""]["pieces root"]
                    layer_hashes = self.info["piece layers"][root]
                    info["layer hashes"] = split_pieces(layer_hashes, SHA256)

            else:
                self.walk_file_tree(val, partials + [key])

    def feeder(self):
        """Check if content hashes match thos in a torrent file."""
        tally = matched = 0
        for result in FeedChecker(self.paths, self.piece_length,
                                  self.fileinfo, self.pieces):
            tally += 1
            matched += 1 if result[0] else 0
            if self.hook_status is not None:
                self.hook_status(*result)

        self.result = str(int((matched / tally) * 100))
        self.log_msg("%s %% of torrent content is available", self.result)

    def hasher(self):
        """Check if file hashes match those in a torrent file.

        Args:
            version (`int`): Meta Version for this torrent file.
        """
        meta_hasher = V2Hash if self.version == 2 else HybridHash
        tally = equal = 0
        for result in Hasher(self.paths, self.piece_length,
                             self.fileinfo, meta_hasher):
            tally += 1
            equal += 1 if result[0] else 0
            if self.hook_status is not None:
                self.hook_status(*result)

        self.result = str(int((equal / tally) * 100))
        self.log_msg("%s %% of torrent content available", self.result)


def check_meta_version(info):
    """Find the meta version for .torrent file.

    Check .torrent file properties to determine which
    protocol version was used to create the .torrent file.

    Args:
        info (`dict`): info dictionary from .torrent file.

    Returns:
        version (`int`): The version number.
    """
    if "meta version" in info and "file tree" in info:
        if "pieces" in info:
            return 3
        return 2
    return 1


def split_pieces(pieces, hash_size):
    """Split bytes into 20 piece chuncks for sha1 digest.

    Args:
        pieces (`bytes`): Initial data.

    Returns:
        lst (`list`): Pieces broken into groups of 20 bytes.
    """
    lst = []
    for i in range(hash_size, len(pieces), hash_size):
        lst.append(pieces[i - hash_size:i])
    return lst
