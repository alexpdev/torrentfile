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
"""Module for Checker class, which validates .torrents.

Classes:
    Checker (`object`): Matches .torrent files with files/folder content
"""

import logging
import os

import pyben

from .hybrid import HybridHash
from .metafile import Feeder
from .metafile2 import V2Hash


class Checker:
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

    _callbacks = []

    def __init__(self, metafile, location):
        """Check a given file or directory to see if it matches a torrentfile.

        Constructor for the .torrent checker/validator.
        """
        self.metafile = metafile
        self.location = location
        self.meta = {}
        self.info = {}
        self.total = 0
        self.piece_length = None
        self.name = None
        self.paths = []
        self.fileinfo = {}
        self.output = ""

    @classmethod
    def add_callback(cls, callback):
        """Register Callback function for displaying progress updates."""
        cls._callbacks.append(callback)

    def decode_metafile(self):
        """Decode bencoded data inside .torrent file."""
        terms = pyben.load(self.metafile)
        self.outmsg("Decoded bencoded data from meta file.")
        for key, val in terms.items():
            self.meta[key] = val
            self.outmsg(f"Meta Dict: {key} = {val}")
            if key == "info":
                for key1, val1 in val.items():
                    self.info[key1] = val1
                    self.outmsg(f"Info Dict: {key1} = {val1}")
        self.name = self.info["name"]
        self.piece_length = self.info["piece length"]
        if "pieces" in self.info:
            self.outmsg("Found Pieces in Info Dict.")
            self.pieces = self.info["pieces"]

    def outmsg(self, text):
        """Generate Text output for notifying users of progress updates."""
        logging.info(text)
        self.output = "\n".join([self.output, text])
        for callback in self._callbacks:
            callback(text)

    def get_paths(self):
        """Get list of paths from files list inside .torrent file."""
        if "file tree" in self.info:
            self.outmsg("File Tree found in Info Dict")
            paths = parse_filetree(self.info["file tree"])
            self.outmsg(f"{paths} parsed from file tree")
            for path, val in paths.items():
                self.paths.append(path)
                self.total += val["length"]
            self.fileinfo = paths
        elif "files" in self.info:
            self.outmsg("Files found in info dict.")
            for item in self.info["files"]:
                size = item["length"]
                self.total += size
                path = os.path.join(*item["path"])
                self.paths.append(path)
                self.fileinfo[path] = size
        else:
            self.paths.append(self.info["name"])
            self.total = self.info["length"]
            self.fileinfo[self.info["name"]] = self.info["length"]
        self.outmsg(f"Total size of all files = {self.total}")
        self.outmsg(f"File Information = {self.fileinfo}")

    def _check_path(self, paths):
        """Check if paths exist.

        Args:
          paths (`list`): Paths to torrent files contents.

        Returns:
          `str`: "Complete" after finishing.
        """
        stats = {"size": 0, "exist": 0}
        for part, path in paths:
            if os.path.exists(path):
                stats["exist"] += 1
                size = os.path.getsize(path)
                if size == self.fileinfo[part]:
                    stats["size"] += 1
        if "meta version" not in self.info and "file tree" not in self.info:
            text = "Detected Bittorrent v1 format."
            self.outmsg(text)
            lst = []
            partials = [i[0] for i in paths]
            if "files" in self.info:
                for item in self.info["files"]:
                    path = os.path.join(*item["path"])
                    lst.append(paths[partials.index(path)][1])
            else:
                lst = [paths[0][1]]
            pieces = self.info["pieces"]
            arr = bytearray()
            for piece in Feeder(lst, self.piece_length, self.total):
                arr.extend(piece)
            if arr == pieces:
                status = "100%"
                text = f"Content matches {status} to .torrent file."
                self.outmsg(text)
                return status
            total = 0
            for path in lst:
                total += os.path.getsize(path)
            status = str(int((total / self.total) * 100)) + "%"
            text = f"Content matches {status} to .torrent file."
            self.outmsg(text)
            return status
        if "pieces" in self.info:
            hasher = HybridHash
            text = "Detected Bittorrent v1 & v2 Hybrid Format."
            self.outmsg(text)
        else:
            hasher = V2Hash
            text = "Detected Bittorrent v2 Format."
            self.outmsg(text)
        matches = []
        for part, path in paths:
            if os.path.exists(path):
                filehash = hasher(path, self.piece_length)
                if filehash.root == self.fileinfo[part]["pieces root"]:
                    matches.append(path)
        if len(matches) == len(paths):
            status = "100%"
            text = f"{status} match for File Hash {path}"
            self.outmsg(text)
            return status
        total = 0
        for path in [i[1] for i in paths]:
            total += os.path.getsize(path)
        status = str(int((total + 1 / self.total + 1) * 100)) + "%"
        text = f"Content matches {status} to .torrent file."
        self.outmsg(text)
        return status

    def check_path(self):
        """Check if path exists and is the correct size and hash.

        Returns:
            status (`str`): Indicating process has completed.
        """
        paths = []
        self.outmsg(f"Torrent File = {self.metafile}")
        self.outmsg(f"Search Dir = {self.location}")
        if os.path.basename(self.location) == self.name:
            if os.path.isfile(self.location):
                paths.append((self.name, self.location))
                text = f"Found single file: {self.location}"
                self.outmsg(text)
                return self._check_path(paths)
            for path in self.paths:
                full = os.path.join(self.location, path)
                paths.append((path, full))
            text = f"Found matching directory: {self.location}"
            self.outmsg(text)
            return self._check_path(paths)
        text = "Searching for matching content in destination directory."
        self.outmsg(text)
        for item in os.listdir(self.location):
            if item == self.name:
                text = f"Found Matching Torrent Content = {item}"
                self.outmsg(text)
                self.location = os.path.join(self.location, item)
                for path in self.paths:
                    full = os.path.join(self.location, path)
                    paths.append((path, full))
                return self._check_path(paths)
        text = ("Could not find matching content in this directory.")
        self.outmsg(text)
        return None

    def check(self):
        """Check if all components work as expected.

        Returns:
            status (`str`): Percentage of .torrent file download completed.
        """
        self.outmsg("Begin decoding .torrent file.")
        self.decode_metafile()
        self.get_paths()
        status = self.check_path()
        return status


def parse_filetree(filetree):
    """Traverse File Tree dictionary and extract data.

    Args:
        filetree (`dict`): file tree dictionary embedded in .torrent

    Returns:
        paths (`dict`): flattened filetree with data.
    """
    paths = {}
    for key, value in filetree.items():
        if key == "":
            if "attr" not in value:
                paths[key] = value
        else:
            out = parse_filetree(filetree[key])
            for k, v in out.items():
                if k == "":
                    paths[key] = v
                else:
                    paths[os.path.join(key, k)] = v
    return paths
