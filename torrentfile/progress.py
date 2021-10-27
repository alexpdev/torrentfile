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

    def __init__(self, paths, piece_length, pieces, fileinfo):
        """Generate hashes of piece length data from filelist contents."""
        self.piece_length = piece_length
        self.paths = paths
        self.pieces = pieces
        self.fileinfo = fileinfo
        self.index = 0
        self.piece_count = 0
        self.iterator = None

    def __iter__(self):
        """Assign iterator and return self."""
        if not self.iterator:
            self.iterator = self.iter_pieces()
        return self

    def __next__(self):
        """Yield back result of comparison."""
        partial = next(self.iterator)
        chunck = sha1(partial).digest()  # nosec
        piece = self.pieces[self.piece_count]
        self.piece_count += 1
        if chunck == piece:
            return True
        return False

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
                for blank in self.gen_blanks(partial):
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

    def gen_blanks(self, partial):
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


class HybridChecker:
    """Construct the HybridChecker.

    Verify that root hashes of content files match the .torrent files.

    Args:
      paths (`list`): List of files.
      piece_length (`int`): Size of chuncks to split the data into.
      fileinfo (`dict`): Info from .torrent file being checked.
    """

    def __init__(self, paths, piece_length, fileinfo):
        """Construct a HybridChecker instance."""
        self.paths = paths
        self.piece_length = piece_length
        self.fileinfo = fileinfo
        self.iterator = None

    def __iter__(self):
        """Assign iterator and return self."""
        if not self.iterator:
            self.iterator = self.iter_paths(HybridHash)
        return self

    def __next__(self):
        """Provide the result of comparison."""
        result = next(self.iterator)
        size, final = result
        return size, final

    def iter_paths(self, hasher):
        """Iterate through and compare root file hashes to .torrent file.

        Args:
            hasher (class): The class user to caluclate root hash.

        Yields:
            results (`tuple`): The size of the file and result of match.
        """
        for path in self.paths:
            size = self.fileinfo[path]["length"]
            if not os.path.exists(path):
                yield size, False
                continue
            result = hasher(path, self.piece_length)
            if result.root == self.fileinfo[path]["pieces root"]:
                yield size, True
            else:
                yield size, False


class V2Checker(HybridChecker):
    """Construct the V2Checker.

    Verify that root hashes of content files match the .torrent files.

    Args:
      paths (`list`): List of files.
      piece_length (`int`): Size of chuncks to split the data into.
      fileinfo (`dict`): Info from .torrent file being checked.
    """

    def __init__(self, *args):
        """Construct a V2Checker Instance for validating a torrent file."""
        super().__init__(*args)

    def __iter__(self):
        """Assign iterator and return self."""
        if not self.iterator:
            self.iterator = self.iter_paths(V2Hash)
        return self


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

    logging_hook = None
    progress_hook = None

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
    def register_hooks(cls, hook1, hook2):
        """Register hooks from 3rd party programs to access generated info.

        Classmethod Args:
            hook1 (`function`): callback function for the logging feature.
            hook2 (`function`): callback function for update progress.
        """
        cls.logging_hook = hook1
        cls.progress_hook = hook2

    def parse_metafile(self):
        """Flatten Meta dictionary of .torrent file.

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
        if self.logging_hook is not None:
            if len(args) == 1:
                msg = args[0]
            elif len(args) == 2:
                msg = args[0] % args[1]
            elif len(args) >= 3:
                msg = (args[0] % tuple(args[1:]))
            if msg:
                self.logging_hook(msg)

    def find_root(self):
        """Find the contents root.

        If the path specified is not the root, then
        search the provided path for content.

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
            self.pieces = split_pieces(self.info["pieces"])
            return self.checkerv1()

        if os.path.isfile(self.root):
            self.log_msg("Single file torrent detected.")
            meta = self.info["file tree"][self.name][""]
            self.fileinfo[self.root] = {
                "prtial": self.name,
                "length": meta["length"],
                "pieces root": meta["pieces root"]
            }
            self.total += meta["length"]
            self.paths.append(self.root)
        else:
            self.walk_file_tree(self.info["file tree"], [])

        return self.checker(self.version)

    def walk_file_tree(self, tree, partials):
        """Traverse File Tree dictionary.

        Extract full pathnames, length, and root hash for each file
        included in the .torrent file.

        Args:
            tree (`dict`): File Tree dict extracted from torrent file.
            partials (`list`): list of intermediate pathnames.
        """
        for key, val in tree.items():
            if "" in val:
                path = os.path.join(self.root, *partials, key)
                self.log_msg("Adding %s to file collection.", path)
                self.paths.append(path)
                self.fileinfo[path] = val[""]
                self.total += val[""]["length"]
                self.fileinfo[path]["partial"] = key
            else:
                self.walk_file_tree(val, partials + [key])

    def checkerv1(self):
        """Check if content hashes match thos in a torrent file."""
        total = len(self.pieces)
        tally = matched = 0
        for result in FeedChecker(self.paths, self.piece_length,
                                  self.pieces, self.fileinfo):
            tally += 1
            matched += 1 if result else 0
            if self.progress_hook:
                self.progress_hook(total, tally, matched)

        self.log_msg("%s percent Completed", str(int((matched / total) * 100)))
        self.result = str(int((matched / total) * 100))

    def checker(self, version):
        """Check if file hashes match those in a torrent file.

        Args:
            version (`int`): Meta Version for this torrent file.
        """
        checker = V2Checker if version == 2 else HybridChecker
        total = self.total
        tally = equal = 0
        for result in checker(self.paths, self.piece_length, self.fileinfo):
            size, match = result
            tally += size
            equal += size if match else 0
            if self.progress_hook:
                self.progress_hook(total, tally, equal)

        self.log_msg("%s percent Completed", str(int((equal / total) * 100)))
        self.result = str(int((equal / total) * 100))


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


def split_pieces(pieces):
    """Split bytes into 20 piece chuncks for sha1 digest.

    Args:
        pieces (`bytes`): Initial data.

    Returns:
        lst (`list`): Pieces broken into groups of 20 bytes.
    """
    lst = []
    for i in range(20, len(pieces), 20):
        if i > len(pieces) - 20:
            lst.append(pieces[i:])
        else:
            lst.append(pieces[i - 20:i])
    return lst
