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

from torrentfile import TorrentFile, TorrentFileV2


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
        for k, v in cls.__dict__.items():
            print(k, v)
            if k in cls.kwargs:
                if isinstance(v, bool):
                    v = 1 if v else 0
                cls.kwargs[k] = v
        return cls.kwargs

    @classmethod
    def create_torrentfile(cls):
        cls.compile_kwargs()
        torrentfile = TorrentFile
        if hasattr(cls, "version") and cls.version == 2:
            torrentfile = TorrentFileV2
        torrentfile = torrentfile(**cls.kwargs)
        torrentfile.assemble()
        torrentfile.write()


class Parser(argparse.ArgumentParser):
    def __init__(
        self, prog="torrentfile", description="Torrentfile CLI", prefix_chars="-"
    ):
        print(prog)
        super().__init__(self, prog, description=description, prefix_chars=prefix_chars)
        self.namespace = CLI
        self.add_args()

    def parse_args(self, args):
        super().parse_args(args, self.namespace)
        self.namespace.create_torrentfile()
        return True

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


def main(args):
    parser = Parser()
    return parser.parse_args(args)


if __name__ == "__main__":
    args = sys.argv[1:]
    main(args)
