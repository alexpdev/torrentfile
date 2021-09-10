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

import sys
import argparse
from torrentfile import __version__, TorrentFile, TorrentFileV2


class Cli:
    """CLI.

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

    def compile_kwargs(self):
        """### compile_kwargs

        Returns
        -----------
        - ckwargs: dict
            - : keyword args for MetaFile Class Init.
        """
        cdict, ckwargs = vars(self), self.kwargs
        for item in ckwargs:
            val = cdict[item]
            if val in [True, False]:
                ckwargs[item] = 1 if val else 0
            elif val and item == "piece_length":
                ckwargs[item] = int(val)
            else:
                ckwargs[item] = val
        return ckwargs

    def create_torrentfile(self):
        """create_torrentfile."""
        self.compile_kwargs()
        torrentfile = TorrentFileV2 if self.version else TorrentFile
        torrentfile = torrentfile(**self.kwargs)
        torrentfile.assemble()
        output = torrentfile.write()
        return output


class Parser(argparse.ArgumentParser):
    """Parser."""

    def __init__(
        self, prog="torrentfile", description="Torrentfile CLI", prefix_chars="-"
    ):
        """__init__.

        #### Initialize Parser class.

        Parameters
        ----------
        - prog : str
            - Name of the program
        - description : str
            - short summary of program functionality
        - prefix_chars : str
            - string containing all characters used as flag prefixes on command line
        """
        super().__init__(self, prog, description=description, prefix_chars=prefix_chars)
        self.name = prog
        self.version = __version__
        self.namespace = Cli()
        self.add_args()

    def parse_args(self, args):
        """## parse_args.

        #### Parse input arguments from command line.

        Parameters
        ----------
        - args : list[str]
            - List of arguments

        Returns
        ---------
        - output : tuple
            - Path to torrentfile, and meta dictionary
        """
        super().parse_args(args, self.namespace)
        output = self.namespace.create_torrentfile()
        return output
    def add_args(self):
        """add_args."""
        self.add_arguement(
            "--version",
            action="version",
            version=f"{self.name} v{self.version}",
            help="Display program version."
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
            "--tracker",
            "--announce",
            action="extend",
            nargs="+",
            help='"--tracker [url1] [url2]..."  add torrent tracker(s).',
            dest="announce",
            metavar="url",
        )
        self.add_argument(
            "--v2",
            "--version2",
            action="store_true",
            help="use Bittorrent V2 protocol if missing V1 is assumed",
            dest="version",
        )


def main(args):
    """main.

    Parameters
    ----------
    - args : list[str]
        - sys.argv strings

    Returns
    ---------
    - tuple :
        - outfile, dictionary
    """
    parser = Parser()
    outfile, meta = parser.parse_args(args)
    return (outfile, meta)


if __name__ == "__main__":
    args = sys.argv[1:]
    main(args)
    print("success")
