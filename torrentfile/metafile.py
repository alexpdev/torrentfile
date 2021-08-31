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
from datetime import datetime

from torrentfile.feeder import Feeder
from torrentfile.utils import Bendecoder, Benencoder, path_stat
from torrentfile.exceptions import MissingPathError

timestamp = lambda: int(datetime.timestamp(datetime.now()))


class TorrentFile:
    """Class for creating Bittorrent meta files."""

    def __init__(
        self,
        path=None,
        piece_length=None,
        announce=None,
        private=None,
        source=None,
        comment=None,
        outfile=None,
        created_by=None,
    ):
        """Constructor for *Torrentfile* class.

        Args:

            * path (str): path to torrent file or directory.
            * piece_length (int): size of each piece of torrent data.
            * created_by (str): creator.
            * announce (str): tracker url.
            * private (int): 1 if private torrent else 0.
            * source (str): source tracker.
            * comment (str): comment string.
            * outfile (str): path to write metfile to.
        """
        if not path:
            raise MissingPathError
        self.base = path
        self.name = os.path.basename(path)
        self.piece_length = piece_length
        self.announce = announce
        self.private = private
        self.source = source
        self.length = None
        self.comment = comment
        self.outfile = outfile
        self.created_by = created_by
        self.files = []
        self.info = {}
        self.meta = {}

    def _assemble_infodict(self):
        """Create info dictionary.

        Returns:

            * dict: info dictionary.
        """
        filelist, size, piece_length = path_stat(self.base)
        # create dictionary keys for available fields.
        # add comment
        if self.comment:
            self.info["comment"] = self.comment
        # if single file, add 'length' key otherwise
        if os.path.isfile(self.base):
            self.info["length"] = size
        else:
            self.files = self.info["files"] = [
                {
                    "length": os.path.getsize(p),
                    "path": os.path.relpath(p, self.base).split(os.sep),
                }
                for p in filelist
            ]
        self.info["name"] = self.name
        if not self.piece_length:
            self.info["piece length"] = self.piece_length = piece_length
        else:
            self.info["piece length"] = self.piece_length
        feeder = Feeder(filelist, self.piece_length, size, sha256=False)
        pieces = bytearray()
        for piece in feeder:
            pieces.extend(piece)
        self.info["pieces"] = pieces
        if self.private:
            self.info["private"] = self.private
        if self.source:
            self.info["source"] = self.source
        return self.info

    def assemble(self):
        """*assemble* Assemble components of torrent metafile.

        Raises:

            * MissingTracker: Announce field is required for all torrents.

        Returns:

            * `dict`: metadata dictionary for torrent file
        """
        if self.announce:
            # if announce is a string assign it to announce key in meta dict
            if isinstance(self.announce, str):
                self.meta["announce"] = self.announce
            # otherwise it must be a iterable then assign first item to
            # announce key and the rest to announce_list key in info dict
            else:
                self.meta["announce"] = self.announce[0]
                if len(self.announce) > 1:
                    self.info["announce list"] = self.announce[1:]

        self.meta["created by"] = "torrentfile"
        self.meta["creation date"] = timestamp()
        self.meta["info"] = self._assemble_infodict()

        encoder = Benencoder()
        self.data = encoder.encode(self.meta)

        return self.data

    def write(self, outfile=None):
        """*self.write(outfile)* Write assembled data to .torrent file.

        Args:

            * outfile (`str`): path to save location. default = None

        Returns:

            * `bytes`: data writtend to .torrent file
        """
        if outfile:
            self.outfile = outfile
        elif not self.outfile:
            self.outfile = self.info["name"] + ".torrent"
        with open(self.outfile, "wb") as fd:
            fd.write(self.data)
        return (self.outfile, self.meta)


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
        fd = open(self.metafile, "rb").read()
        decoder = Bendecoder()
        dictt = decoder.decode(fd)
        for k, v in dictt.items():
            self.meta[k] = v
            if k == "info":
                for k1, v1 in v.items():
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
            if pieces[: len(digest)] == digest:
                pieces = pieces[len(digest) :]
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
