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
######################################################################

import os
from torrentfile.utils import Bendecoder
from torrentfile.feeder import Feeder

class Checker:
    """Checks a given file or directory to see if it matches a torrentfile."""

    def __init__(self, metafile, location):
        """__init__ Public constructor for Checker class instance.

        Args:
            metafile: path to ".torrent" file.
            location: path where the content is located in filesystem.

        Example:
            >> metafile = "/path/to/torrentfile/content_file_or_dir.torrent"
            >> location = "/path/to/location"
            >> os.path.exists("/path/to/location/content_file_or_dir")
            Out: True
            >> checker = Checker(metafile, location)
        """
        self.metafile = metafile
        self.location = location
        self.meta = {}
        self.info = {}
        self.total = 0
        self.piece_length = None
        self.files = None
        self.length = None
        self.name = None
        self.paths = []
        self.fileinfo = {}

    def decode_metafile(self):
        """decode_metafile Decode bencoded data inside .torrent file."""
        fd = open(self.metafile,"rb").read()
        decoder = Bendecoder()
        dictt = decoder.decode(fd)
        for k,v in dictt.items():
            self.meta[k] = v
            if k == "info":
                for k1,v1 in v.items():
                    self.info[k1] = v1
        self.piece_length = self.info["piece length"]
        self.pieces = self.info["pieces"]
        self.name = self.info["name"]
        if "length" in self.info:
            self.length = self.info["length"]
        else:
            self.files = self.info["files"]
        return

    def get_paths(self):
        """get_paths  Get list of paths from files list inside .torrent file."""
        if self.length is not None:
            self.paths.append(self.name)
            self.fileinfo[self.name] = self.length
        else:
            for item in self.files:
                size = item["length"]
                self.total += size
                path = os.path.join(*item["path"])
                self.paths.append(path)
                self.fileinfo[path] = size
        return self.paths

    def _check_path(self, paths):
        feeder = Feeder(paths, self.piece_length, self.total, sha256=False)
        pieces = bytes.fromhex(self.pieces)
        counter = 0
        for digest in feeder:
            if pieces[:len(digest)] == digest:
                pieces = pieces[len(digest):]
                counter += 1
            else:
                print("Number of matching pieces = ", counter)
        return "complete"

    def check_path(self):
        base = os.path.join(self.location, self.name)
        if os.path.isfile(base):
            paths = [base]
        else:
            paths = [os.path.join(base, i) for i in self.paths]
        return self._check_path(paths)

    def check(self):
        self.decode_metafile()
        self.get_paths()
        status = self.check_path()
        print(status)
