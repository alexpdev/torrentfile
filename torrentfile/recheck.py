#! /usr/bin/python3
# -*- coding: utf-8 -*-

##############################################################################
#    Copyright (C) 2021-current alexpdev
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
##############################################################################
"""
Module container Checker Class.

The CheckerClass takes a torrentfile and tha path to it's contents.
It will then iterate through every file and directory contained
and compare their data to values contained within the torrent file.
Completion percentages will be printed to screen for each file and
at the end for the torrentfile as a whole.
"""

import logging
import os
from hashlib import sha1, sha256  # nosec
from pathlib import Path
from threading import Thread

import pyben

from torrentfile.hasher import FileHasher, HasherHybrid, HasherV2
from torrentfile.mixins import ProgMixin, waiting
from torrentfile.utils import MissingPathError

SHA1 = 20
SHA256 = 32
BLOCK_SIZE = 2**14  # 16KiB

logger = logging.getLogger(__name__)


class Checker(ProgMixin):
    """
    Check a given file or directory to see if it matches a torrentfile.

    Public constructor for Checker class instance.

    Parameters
    ----------
    metafile : str
        Path to ".torrent" file.
    path : str
        Path where the content is located in filesystem.

    Example
    -------
        >> metafile = "/path/to/torrentfile/content_file_or_dir.torrent"
        >> location = "/path/to/location"
        >> os.path.exists("/path/to/location/content_file_or_dir")
        Out: True
        >> checker = Checker(metafile, location)
    """

    _hook = None

    def __init__(self, metafile: str, path: str):
        """
        Validate data against hashes contained in .torrent file.

        Parameters
        ----------
        metafile : str
            path to .torrent file
        path : str
            path to content or contents parent directory.
        """
        if not os.path.exists(metafile):
            raise FileNotFoundError
        meta = []
        thread = Thread(target=pyben.loadinto, args=(metafile, meta))
        thread.start()
        self.last_log = None
        self.log_msg("Checking: %s, %s", metafile, path)
        self.metafile = metafile
        self.total = 0
        self.paths = []
        self.fileinfo = {}
        thread2 = Thread(target=waiting, args=("Extracting metadata", meta))
        if not meta:  # pragma: nocover
            thread2.start()
            thread2.join()
        self.meta = meta[0]
        self.info = self.meta["info"]
        self.name = self.info["name"]
        self.piece_length = self.info["piece length"]

        if "meta version" in self.info:
            if "pieces" in self.info:
                self.meta_version = 3
            else:
                self.meta_version = 2
        else:
            self.meta_version = 1

        self.root = self.find_root(path)
        self.check_paths()

    @classmethod
    def register_callback(cls, hook):
        """
        Register hooks from 3rd party programs to access generated info.

        Parameters
        ----------
        hook : function
            callback function for the logging feature.
        """
        cls._hook = hook

    def piece_checker(self):
        """
        Check individual pieces of the torrent.

        Returns
        -------
        HashChecker | FeedChecker
            Individual piece hasher.
        """
        if self.meta_version == 1:
            return FeedChecker
        return HashChecker

    def results(self):
        """
        Generate result percentage and store for future calls.
        """
        responses = []
        for response in self.iter_hashes():
            responses.append(response)

        self.log_msg(
            "Final result for %s recheck:  %s", self.metafile, self._result
        )
        return self._result

    def log_msg(self, *args, level=logging.INFO):
        """
        Log message `msg` to logger and send `msg` to callback hook.

        Parameters
        ----------
        args : dict
            formatting args for log message
        level : int
            Log level for this message; default=`logging.INFO`
        """
        message = args[0]
        if len(args) >= 3:
            message = message % tuple(args[1:])
        elif len(args) == 2:
            message = message % args[1]

        # Repeat log messages should be ignored.
        if message != self.last_log:
            self.last_log = message
            logger.log(level, message)
            if self._hook and level == logging.INFO:
                self._hook(message)

    def find_root(self, path: str) -> str:
        """
        Check path for torrent content.

        The path can be a relative or absolute filesystem path.  In the case
        where the content is a single file, the path may point directly to the
        the file, or it may point to the parent directory.  If content points
        to a directory.  The directory will be checked to see if it matches
        the torrent's name, if not the directories contents will be searched.
        The returned value will be the absolute path that matches the torrent's
        name.

        Parameters
        ----------
        path : str
            root path to torrent content

        Returns
        -------
        str
            root path to content
        """
        if not os.path.exists(path):
            self.log_msg("Could not locate torrent content %s.", path)
            raise FileNotFoundError(path)

        root = Path(path)
        if root.name == self.name:
            self.log_msg("Content found: %s.", str(root))
            return root

        if self.name in os.listdir(root):
            return root / self.name

        self.log_msg("Could not locate torrent content in: %s", str(root))
        raise FileNotFoundError(root)

    def check_paths(self):
        """
        Gather all file paths described in the torrent file.
        """
        finfo = self.fileinfo

        if "length" in self.info:
            self.log_msg("%s points to a single file", self.root)
            self.total = self.info["length"]
            self.paths.append(str(self.root))

            finfo[0] = {
                "path": self.root,
                "length": self.info["length"],
            }

            if self.meta_version > 1:
                root = self.info["file tree"][self.name][""]["pieces root"]
                finfo[0]["pieces root"] = root

            return

        # Otherwise Content is more than 1 file.
        self.log_msg("%s points to a directory", self.root)
        if self.meta_version == 1:

            for i, item in enumerate(self.info["files"]):
                self.total += item["length"]
                base = os.path.join(*item["path"])

                self.fileinfo[i] = {
                    "path": str(self.root / base),
                    "length": item["length"],
                }

                self.paths.append(str(self.root / base))
            return

        self.walk_file_tree(self.info["file tree"], [])

    def walk_file_tree(self, tree: dict, partials: list):
        """
        Traverse File Tree dictionary to get file details.

        Extract full pathnames, length, root hash, and layer hashes
        for each file included in the .torrent's file tree.

        Parameters
        ----------
        tree : dict
            File Tree dict extracted from torrent file.
        partials : list
            list of intermediate pathnames.
        """
        for key, val in tree.items():

            # Empty string means the tree's leaf is value
            if "" in val:

                base = os.path.join(*partials, key)
                roothash = None
                length = val[""]["length"]
                roothash = None if not length else val[""]["pieces root"]
                full = str(self.root / base)
                self.fileinfo[len(self.paths)] = {
                    "path": full,
                    "length": length,
                    "pieces root": roothash,
                }
                self.paths.append(full)
                self.total += length
            else:
                self.walk_file_tree(val, partials + [key])

    def iter_hashes(self) -> tuple:
        """
        Produce results of comparing torrent contents piece by piece.

        Yields
        ------
        chunck : bytes
            hash of data found on disk
        piece : bytes
            hash of data when complete and correct
        path : str
            path to file being hashed
        size : int
            length of bytes hashed for piece
        """
        matched = consumed = 0
        checker = self.piece_checker()
        for chunk, piece, path, size in checker(self):
            consumed += size
            matching = 0
            if chunk == piece:
                matching += size
                matched += size
            yield chunk, piece, path, size
            total_consumed = str(int(consumed / self.total * 100))
            percent_matched = str(int(matched / consumed * 100))
            self.log_msg(
                "Processed: %s%%, Matched: %s%%",
                total_consumed,
                percent_matched,
                level=logging.DEBUG,
            )
        self._result = (matched / consumed) * 100 if consumed > 0 else 0


class FeedChecker(ProgMixin):
    """
    Validates torrent content.

    Seemlesly validate torrent file contents by comparing hashes in
    metafile against data on disk.

    Parameters
    ----------
    checker : object
        the checker class instance.
    hasher : Any
        hashing class for calculating piece hashes. default=None
    """

    def __init__(self, checker: Checker):
        """
        Generate hashes of piece length data from filelist contents.
        """
        self.piece_length = checker.piece_length
        self.paths = checker.paths
        self.pieces = checker.info["pieces"]
        self.fileinfo = checker.fileinfo
        self.piece_map = {}
        self.index = 0
        self.piece_count = 0
        self.it = None

    def __iter__(self):
        """
        Assign iterator and return self.
        """
        self.it = self.iter_pieces()
        return self

    def __next__(self):
        """
        Yield back result of comparison.
        """
        try:
            partial = next(self.it)
        except StopIteration as itererror:
            raise StopIteration from itererror

        chunck = sha1(partial).digest()  # nosec
        start = self.piece_count * SHA1
        end = start + SHA1
        piece = self.pieces[start:end]
        self.piece_count += 1
        path = self.paths[self.index]
        return chunck, piece, path, len(partial)

    def iter_pieces(self):
        """
        Iterate through, and hash pieces of torrent contents.

        Yields
        ------
        piece : bytes
            hash digest for block of torrent data.
        """
        partial = bytearray()
        for i, path in enumerate(self.paths):
            total = self.fileinfo[i]["length"]
            self.prog_start(total, path, unit="bytes")
            self.index = i
            if os.path.exists(path):
                for piece in self.extract(path, partial):
                    self.prog_update(len(piece))
                    if (len(piece) == self.piece_length) or (
                        i + 1 == len(self.paths)
                    ):
                        yield piece
                    else:
                        partial = piece

            else:
                length = self.fileinfo[i]["length"]
                for pad in self._gen_padding(partial, length):
                    if len(pad) == self.piece_length:
                        yield pad
                    else:
                        partial = pad
            self.prog_close()

    def extract(self, path: str, partial: bytearray) -> bytearray:
        """
        Split file paths contents into blocks of data for hash pieces.

        Parameters
        ----------
        path : str
            path to content.
        partial : bytes
            any remaining content from last file.

        Returns
        -------
        bytearray
            Hash digest for block of .torrent contents.
        """
        read = 0
        length = self.fileinfo[self.index]["length"]
        partial = bytearray() if len(partial) == self.piece_length else partial
        if path not in self.paths:  # pragma: no cover
            raise MissingPathError(path)
        with open(path, "rb") as current:
            while True:
                bitlength = self.piece_length - len(partial)
                part = bytearray(bitlength)
                amount = current.readinto(part)
                read += amount
                partial.extend(part[:amount])
                if amount < bitlength:
                    if amount > 0 and read == length:
                        self.prog_update(amount)
                        yield partial
                    break
                self.prog_update(amount)
                yield partial
                partial = bytearray(0)
        if length != read:
            for pad in self._gen_padding(partial, length, read):
                yield pad

    def _gen_padding(self, partial: bytes, length: int, read=0) -> bytes:
        """
        Create padded pieces where file sizes do not match.

        Parameters
        ----------
        partial : bytes
            any remaining data from last file processed.
        length : int
            size of space that needs padding
        read : int
            portion of length already padded

        Yields
        ------
        bytes
            A piece length sized block of zeros.
        """
        while read < length:
            left = self.piece_length - len(partial)
            if length - read > left:
                padding = bytearray(left)
                partial.extend(padding)
                yield partial
                read += left
                partial = bytearray(0)
            else:
                partial.extend(bytearray(length - read))
                read = length
                yield partial


class HashChecker(ProgMixin):
    """
    Verify that root hashes of content files match the .torrent files.

    Parameters
    ----------
    checker : Object
        the checker instance that maintains variables.
    hasher : Object
        the version specific hashing class for torrent content.
    """

    def __init__(self, checker: Checker):
        """
        Construct a HybridChecker instance.
        """
        self.checker = checker
        self.paths = checker.paths
        self.piece_length = checker.piece_length
        self.fileinfo = checker.fileinfo
        self.piece_layers = checker.meta["piece layers"]
        self.piece_count = 0
        self.it = None

    def __iter__(self):
        """
        Assign iterator and return self.
        """
        self.it = self.iter_paths()
        return self

    def __next__(self):
        """
        Provide the result of comparison.
        """
        try:
            value = next(self.it)
            return value
        except StopIteration as stopiter:
            raise StopIteration() from stopiter

    def iter_paths(self) -> tuple:
        """
        Iterate through and compare root file hashes to .torrent file.

        Yields
        ------
        results : tuple
            The size of the file and result of match.
        """
        for i, path in enumerate(self.paths):
            info = self.fileinfo[i]
            length, plength = info["length"], self.piece_length
            roothash = info["pieces root"]
            self.prog_start(length, path, unit="bytes")
            if roothash in self.piece_layers:
                pieces = self.piece_layers[roothash]
            else:
                pieces = roothash if roothash else bytes()
            amount = len(pieces) // SHA256

            if not os.path.exists(path):
                for i in range(amount):
                    start = i * SHA256
                    end = start + SHA256
                    piece = pieces[start:end]
                    if length > plength:
                        size = plength
                    else:
                        size = length
                    length -= size
                    self.prog_update(0)
                    block = sha256(bytearray(size)).digest()
                    yield block, piece, path, size

            else:
                hasher = FileHasher(path, plength, progress=0)
                for i, result in enumerate(hasher):
                    if len(result) == 2:
                        print(result)
                        layer, _ = result
                    else:
                        layer = result
                    start = i * SHA256
                    end = start + SHA256
                    piece = pieces[start:end]
                    size = plength if plength < length else length
                    length -= size
                    self.prog_update(size)
                    yield layer, piece, path, size
                if i < amount:
                    for _ in range(amount - i):
                        start = i * SHA256
                        end = start + SHA256
                        piece = pieces[start:end]
                        size = plength if plength < length else length
                        length -= size
                        self.prog_update(0)
                        yield sha256(
                            bytearray(size)
                        ).digest(), piece, path, size
            self.prog_close()
