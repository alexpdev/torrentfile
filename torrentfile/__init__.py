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

"""Torrentfile can create Bittorrent metafiles for any content.

Both Bittorrent v1 and v2 are fully supported. Also included is a torrent
torrent file checker, which can verify a .torrent file is formated correctly
as well as validate files and folders against metadata.

Modules:
    metafile: Creation/Validation of v1 .torrent files.
    metafileV2: Creation/Validation of v2 .torrent files.
    torrentfile: torrentfile's Command Line Interface implementation.
    exceptions: Custom Exceptions used in package.
    utils: Utilities used throughout package.
"""

from torrentfile import utils, metafile, metafileV2, torrentfile, exceptions
from torrentfile.metafile import TorrentFile
from torrentfile.metafileV2 import TorrentFileV2
from torrentfile.torrentfile import main
from torrentfile.utils import (
    path_stat,
    path_size,
    get_piece_length,
    path_piece_length,
    Benencoder,
    Bendecoder,
)

__version__ = "0.2.5"
__author__ = "alexpdev"

__all__ = (
    "metafile",
    "metafileV2",
    "torrentfile",
    "exceptions",
    "main",
    "path_stat",
    "path_size",
    "utils",
    "get_piece_length",
    "path_piece_length",
    "Benencoder",
    "Bendecoder",
    "TorrentFile",
    "TorrentFileV2",
)
