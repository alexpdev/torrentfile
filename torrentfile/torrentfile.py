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
from argparse import ArgumentParser
import torrentfile
from torrentfile.metafile import TorrentFile
from torrentfile.metafileV2 import TorrentFileV2


def main():
    """Initialize Command Line Interface."""
    args = sys.argv[1:]
    d = "Tool for creating, inspecting, or checking Bittorrent metafiles. Both .torrent v1 and v2 files are supported."
    parser = ArgumentParser(sys.argv[0],description=d,prefix_chars="-")

    parser.add_argument(
        "--version",
        action="version",
        version=f"torrentfile v{torrentfile.__version__}",
        help="Display program version then exit immediately.",
    )

    parser.add_argument(
        "--created-by",
        action="store",
        dest="created_by",
        metavar="X",
        help="(optional) Leave out unless specifically instructed otherwise.",
    )

    parser.add_argument(
        "--comment",
        action="store",
        dest="comment",
        metavar="X",
        help="(optional) Include comment in binary data.",
    )

    parser.add_argument(
        "-o",
        "--outfile",
        action="store",
        help="(optional) save output to file.",
        dest="outfile",
        metavar="~/X.torrent",
    )

    parser.add_argument(
        "-p",
        "--path",
        action="store",
        dest="path",
        metavar="~/X",
        help="Path to file of directory of torrent contents.",
    )

    parser.add_argument(
        "--piece-length",
        action="store",
        dest="piece_length",
        metavar="X",
        help="(optional) Size of individual pieces of the torrent data.",
    )

    parser.add_argument(
        "--private",
        action="store_true",
        dest="private",
        help="(optional) Torrent will be distributed on a private tracker.",
    )

    parser.add_argument(
        "--source",
        action="store",
        dest="source",
        metavar="X",
        help="(optional) Leave out unless specifically instructed otherwise",
    )

    parser.add_argument(
        "-t",
        "--announce",
        "--tracker",
        action="store",
        dest="announce",
        help='{torrentfile --tracker https://torrent.ubuntu.com/announce} \
                add torrent tracker announce url.',
    )

    parser.add_argument(
        "--announce-list",
        "--tracker-list",
        action="extend",
        dest="announce_list",
        help="{--tracker-list url1 url2...} (optional) additional trackers."
    )

    parser.add_argument(
        "--v2",
        "--meta-version2",
        action="store_true",
        dest="v2",
        help="(optional) work with Bittorrent V2 torrent file.",
    )

    flags = parser.parse_args(args)

    kwargs = {
    "flags": flags,
    "path": flags.path,
    "announce": flags.announce,
    "piece_length": flags.piece_length,
    "source": flags.source,
    "private": flags.private,
    "outfile": flags.outfile,
    "created_by": flags.created_by,
    "comment": flags.comment,
    }

    if flags.v2:
        torrent = TorrentFileV2(flags)
    else:
        torrent = TorrentFile(flags)
    torrent.assemble()
    outfile, meta = torrent.write()
    parser.kwargs = kwargs
    parser.meta = meta
    parser.outfile = outfile
    return parser


if __name__ == "__main__":
    main()
