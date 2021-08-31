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
import argparse
import sys
from torrentfile.metafile import TorrentFile
from torrentfile.metafileV2 import TorrentFileV2


class CLI:

    kwargs = {
        "announce": None,
        "comment": None,
        "created_by": None,
        "path": None,
        "piece_length": None,
        "private": None,
        "source": None,
        "outfile": None,
    }

    @classmethod
    def compile_kwargs(cls):
        cdict = cls.__dict__
        ckwargs = cls.kwargs
        for item in ckwargs:
            if item in cdict:
                val = cdict[item]
                if isinstance(val,bool):
                    ckwargs[item] = 1 if val else 0
                else:
                    ckwargs[item] = val
        return ckwargs

    @classmethod
    def create_torrentfile(cls):
        cls.compile_kwargs()
        torrentfile = TorrentFile
        if hasattr(cls, "version") and cls.version == True:
            torrentfile = TorrentFileV2
        torrentfile = torrentfile(**cls.kwargs)
        torrentfile.assemble()
        output = torrentfile.write()
        return output

class Parser(argparse.ArgumentParser):
    def __init__(
        self, prog="torrentfile", description="Torrentfile CLI", prefix_chars="-"
    ):
        super().__init__(self, prog, description=description, prefix_chars=prefix_chars)
        self.namespace = CLI
        self.add_args()

    def parse_args(self, args):
        super().parse_args(args, self.namespace)
        output = self.namespace.create_torrentfile()
        return output

    def add_args(self):
        self.add_argument(
            "--created-by",
            action="store",
            dest="created_by",
            metavar="X",
            help="leave out unless specifically instructed otherwise",
        )
        self.add_argument(
            "--comment",
            action="store",
            dest="comment",
            metavar="X",
            help="include comment in binary data",
        )
        self.add_argument(
            "-o",
            "--outfile",
            action="store",
            help="save output to file.",
            dest="outfile",
            metavar="~/X.torrent",
        )
        self.add_argument(
            "-p",
            "--path",
            action="store",
            help="Path to file of directory of torrent contents.",
            dest="path",
            metavar="~/X",
        )
        self.add_argument(
            "--piece-length",
            action="store",
            help="Size of individual pieces of the torrent data.",
            dest="piece_length",
            metavar="X",
        )
        self.add_argument(
            "--private",
            action="store_true",
            help="torrent will be distributed on a private tracker",
            dest="private",
        )
        self.add_argument(
            "--source",
            action="store",
            dest="source",
            metavar="X",
            help="leave out unless specifically instructed otherwise",
        )
        self.add_argument(
            "-t",
            "-a",
            action="append",
            nargs="+",
            help='"-t [url]" required for each trackers to be added to tracker list',
            dest="announce",
            metavar="url",
        )
        self.add_argument(
            "-v",
            "--v2",
            "--version2",
            action="store_true",
            help="use Bittorrent V2 protocol if missing V1 is assumed",
            dest="version",
        )

def main(args):
    parser = Parser()
    outfile, meta = parser.parse_args(args)
    return (outfile, meta)

if __name__ == "__main__":
    args = sys.argv[1:]
    main(args)
    print("success")
