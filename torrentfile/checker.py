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
        self.info = {}
        self.total = 0
        self.piece_length = None
        self.name = None
        self.paths = []
        self.fileinfo = {}
        self.output = ""
        self.status = "Unknown."

    @classmethod
    def add_callback(cls, callback):
        """Register Callback function for displaying progress updates."""
        cls._callbacks.append(callback)

    def outmsg(self, text):
        """Generate Text output for notifying users of progress updates."""
        logging.info(text)
        self.output = "\n".join([self.output, text])
        for callback in self._callbacks:
            callback(text)

    def decode_metafile(self):
        """Decode bencoded data inside .torrent file."""
        terms = pyben.load(self.metafile)
        self.outmsg(f"Decoding torrent file: {self.metafile}")
        for key1, val1 in terms.items():
            self.info[key1] = val1
            if key1 == "info":
                for key2, val2 in val1.items():
                    self.info[key2] = val2
        self.name = self.info["name"]
        self.outmsg(f"Torrent name: {self.name}")
        self.piece_length = self.info["piece length"]
        self.outmsg(f"Torrent piece length: {self.piece_length}")
        if "meta version" not in self.info and "pieces" in self.info:
            self.meta_version = 1
        elif "pieces" in self.info and "meta version" in self.info:
            self.meta_version = 3
        else:
            self.meta_version = 2
        self.outmsg(f"Bittorrent meta-version {self.meta_version} detected.")

    def run_procedure(self):
        """Get list of paths from files list inside .torrent file."""
        self.outmsg("Searching for Root Directory.")
        current = os.path.basename(self.location)
        if self.name == current:
            self.outmsg(f"Found root path: {self.location}.")
            return self.check_paths()
        for name in os.listdir(self.location):
            if name == self.name:
                full = os.path.join(self.location, name)
                self.location = full
                self.outmsg(f"Found root path: {self.location}.")
                return self.check_paths()
        self.status = 0
        self.outmsg(f"No torrent content was found in {self.location}?")
        return self.status

    def check_paths(self):
        """Extract and validate file path information from .torrent file."""
        if self.meta_version == 1:
            if os.path.isfile(self.location):
                self.outmsg(f"Single File Torrent: {self.location}")
                length = self.info["length"]
                self.paths.append(self.location)
                self.total = self.info["length"]
                self.fileinfo[self.location] = {
                    "partial": self.name, "length": length
                }
                return self.v1_checker()
            for item in self.info["files"]:
                if "attr" in item:
                    continue
                path = os.path.join(*item["path"])
                self.total += item["length"]
                full = os.path.join(self.location, path)
                self.paths.append(full)
                self.outmsg(f"Torrent includes: {full}, {item['length']}")
                self.fileinfo[full] = {
                    "partial": path, "length": item["length"]
                }
            self.outmsg(f"Torrent total size in bytes: {self.total}")
            return self.v1_checker()
        if os.path.isfile(self.location):
            full = os.path.join(self.location, self.name)
            fileinfo = self.info["file tree"][self.name][""]
            self.paths = [self.location]
            self.fileinfo[self.location] = {
                "partial": self.name,
                "length": fileinfo["length"],
                "pieces root": fileinfo["pieces root"]
            }
            return self.hash_checker()
        paths = parse_filetree(self.info["file tree"])
        for path, details in paths.items():
            full = os.path.join(self.location, path)
            self.outmsg(f"Torrent includes: {full}")
            self.paths.append(full)
            self.total += details["length"]
            self.fileinfo[full] = {
                "partial": path,
                "length": details["length"],
                "pieces root": details["pieces root"]
            }
        return self.hash_checker()

    def v1_checker(self):
        """Verify the contents using Bittorrent v1 Protocol.

        Args:
            pathlst (`list`): list of paths for hashing.

        Returns:
            status (`str`): Text percentage of content downloaded.
        """
        total_pieces = (self.total // self.piece_length) + 1
        num_pieces = total_pieces
        arr = bytearray()
        for piece in Feeder(self.paths, self.piece_length, self.total):
            arr.extend(piece)
            if self.info["pieces"][:len(arr)] == arr:
                num_pieces -= 1
        percentage = int(((total_pieces - num_pieces) / total_pieces) * 100)
        self.status = f"{percentage}%"
        self.outmsg(f"Done: Checker Status = {self.status}")

    def hash_checker(self):
        """Validate files using Bittorrent v2 and hybrid file formats."""
        hasher = V2Hash if self.meta_version == 2 else HybridHash
        total = len(self.paths)
        for item in self.paths:
            if os.path.exists(item):
                filehash = hasher(item, self.piece_length)
                if filehash.root == self.fileinfo[item]["pieces root"]:
                    total -= 1
        percentage = int(((len(self.paths) - total) / len(self.paths)) * 100)
        self.status = f"{percentage}%"
        self.outmsg(f"Done: Checker Status = {self.status}")

    def check(self):
        """Check if all components work as expected.

        Returns:
            status (`str`): Percentage of .torrent file download completed.
        """
        self.decode_metafile()
        self.outmsg(f"Searching {self.location} matching files.")
        status = self.run_procedure()
        return status if status else self.status


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
