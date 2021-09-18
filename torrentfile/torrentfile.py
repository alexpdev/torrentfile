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
"""Main script activated by calls from Command Line."""

import sys
import os
import argparse
import inspect
import torrentfile
from torrentfile.metafile import TorrentFile
from torrentfile.metafileV2 import TorrentFileV2


class Cli:
    """
    Command Line Interface for torrentfile.
    """

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

    def __str__(self):
        """Return string representation of object."""
        return str(self.kwargs)

    def __compile_kwargs(self):
        """Compile kwargs from command line flags."""
        cdict = vars(self)
        for item in self.kwargs:
            val = cdict[item]
            if val in [True, False]:
                self.kwargs[item] = 1 if val else 0
            elif val and item == "piece_length":
                self.kwargs[item] = int(val)
            else:
                self.kwargs[item] = val

    def create_torrentfile(self):
        """Create .torrentfile from input options."""
        self.__compile_kwargs()
        torrentfile = TorrentFileV2 if self.version else TorrentFile
        torrentfile = torrentfile(**self.kwargs)
        torrentfile.assemble()
        self.output = torrentfile.write()


class Parser(argparse.ArgumentParser):
    """
    Parser Initialize command line argument parser.

    Args:
      prog(str): Name of the program
      description(str): Short summary of program functionality.
      prefix_chars(str): Flag prefixes on command line.

    Returns:
      parser obj: Parser instance with runtime information as attributes.

    """

    def __init__(self, prog=sys.argv[0],
                 prefix_chars="-", description="Torrentfile CLI"):
        """
        Parser Initialize command line argument parser.

        Args:
        prog(str): Name of the program
        description(str): Short summary of program functionality.
        prefix_chars(str): Flag prefixes on command line.

        Returns:
        parser obj: Parser instance with runtime information as attributes.

        """
        super().__init__(self, prog, prefix_chars=prefix_chars,
                         description=description)
        self.name = prog
        self.version = torrentfile.__version__
        self.namespace = Cli()
        self.__add_args()

    def parse(self, args):
        """
        Parse input arguments from command line.

        Args:
          args(list of str): List of user supplied arguments.

        """
        self.parse_args(args, self.namespace)
        self.namespace.create_torrentfile()
        outfile, meta = self.namespace.output
        self.outfile = outfile
        self.meta = meta

    def __str__(self):
        """Return string representation of object."""
        return str(self.namespace)

    def __add_args(self):
        """add_args."""
        self.add_argument(
            "--version",
            action="version",
            version=f"{self.name} v{self.version}",
            help="Display program version.",
        )
        self.add_argument(
            "--created-by",
            action="store",
            dest="created_by",
            metavar="X",
            help="Leave out unless specifically instructed otherwise.",
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
            dest="path",
            metavar="~/X",
            help="Path to file of directory of torrent contents.",
        )
        self.add_argument(
            "--piece-length",
            action="store",
            dest="piece_length",
            metavar="X",
            help="Size of individual pieces of the torrent data.",
        )
        self.add_argument(
            "--private",
            action="store_true",
            dest="private",
            help="torrent will be distributed on a private tracker",
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
            dest="announce",
            metavar="url",
            help='"-t url1 url2"  add torrent tracker(s).',
        )
        self.add_argument(
            "--v2",
            "--version2",
            action="store_true",
            dest="version",
            help="use Bittorrent V2 protocol if missing V1 is assumed",
        )


def main():
    """Initialize Command Line Interface."""
    args = sys.argv[1:]
    parser = Parser()
    parser.parse(args)
    dirname = os.path.dirname(os.path.abspath(__file__))
    cli = os.path.join(dirname, "__main__.py")
    return parser





if __name__ == "__main__":
    main()
