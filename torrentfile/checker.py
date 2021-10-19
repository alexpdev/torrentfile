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

    def decode_metafile(self):
        """Decode bencoded data inside .torrent file."""
        terms = pyben.load(self.metafile)
        for key, val in terms.items():
            self.meta[key] = val
            if key == "info":
                for key1, val1 in val.items():
                    self.info[key1] = val1
        self.name = self.info["name"]
        self.piece_length = self.info["piece length"]
        if "pieces" in self.info:
            self.pieces = self.info["pieces"]

    def hook(self, text=None):
        """Create Entry Point for 3rd party programs to hook into."""
        raise NotImplementedError

    def write_output(self, text):
        """Generate Text output for notifying users of progress updates."""
        try:
            self.hook(text=text)
        except NotImplementedError:
            logging.warning(text)
        self.output = "\n".join([self.output, text])

    def get_paths(self):
        """Get list of paths from files list inside .torrent file."""
        if "file tree" in self.info:
            paths = parse_filetree(self.info["file tree"])
            for path, val in paths.items():
                self.paths.append(path)
                self.total += val["length"]
            self.fileinfo = paths
        elif "files" in self.info:
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

    def _check_path(self, paths):
        """Check if paths exist.

        Args:
          paths (`list`): Paths to torrent files contents.

        Returns:
          `str`: "Complete" after finishing.
        """
        if "meta version" in self.info:
            matched = 0
            if "pieces" in self.info:
                text = "Detected Bittorrent v1 & v2 Hybrid Format."
                self.write_output(text)
                hasher = HybridHash
            else:
                text = "Detected Bittorrent v2 Format."
                self.write_output(text)
                hasher = V2Hash
            for path in paths:
                partial = None
                if os.path.exists(path):
                    filehash = hasher(path, self.piece_length)
                    for partial in self.paths:
                        if path == os.path.join(self.location, partial):
                            break
                    if filehash.root == self.fileinfo[partial]["pieces root"]:
                        matched += 1
                        text = f"100% match for File Hash {path}"
                        self.write_output(text)
                    else:
                        text = (f"{filehash.root.hex()} does not match "
                                f"{self.fileinfo[partial]['pieces_root']}")
                        self.write_output(text)
            status = f"{int((matched / len(paths)) * 100)}%"
            self.write_output(status + "matches .torrent file.")
        else:
            text = "Detected Bittorrent v1 Format."
            self.write_output(text)
            hasher = Feeder
            feeder = hasher(paths, self.piece_length, self.total)
            pieces = self.pieces
            total = len(pieces) // 20
            counter = 0
            for digest in feeder:
                diglen = len(digest)
                if pieces[:diglen] == digest:
                    pieces = pieces[diglen:]
                    counter += 1
            status = str(int(counter / total) * 100) + "%"
            self.write_output(status + " matches .torrent file.")
        return status

    def check_path(self):
        """Check if path exists and is the correct size and hash.

        Returns:
            status (`str`): Indicating process has completed.
        """
        if os.path.isfile(self.location):
            if os.path.basename(self.location) == self.name:
                paths = [self.location]
                text = f"Found match: {self.location}"
                self.write_output(text)
                return self._check_path(paths)
        if os.path.basename(self.location) != self.name:
            for item in os.listdir(self.location):
                if item in self.paths:
                    text = f"Found match: {os.path.join(self.location, item)}"
                    self.write_output(text)
                    self.location = os.path.join(self.location, item)
                    break
        paths = [os.path.join(self.location, i) for i in self.paths]
        return self._check_path(paths)

    def check(self):
        """Check if all components work as expected.

        Returns:
            status (`str`): Percentage of .torrent file download completed.
        """
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
