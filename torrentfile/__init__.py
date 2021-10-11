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
    metafile2: Creation/Validation of v2 .torrent files.
    torrentfile: torrentfiles Command Line Interface implementation.
    exceptions: Custom Exceptions used in package.
    utils: Utilities used throughout package.
"""

from .metafile import TorrentFile
from .metafile2 import TorrentFileV2
from .hybrid import TorrentFileHybrid
from .torrentfile import main
from .utils import Benencoder, Bendecoder

__version__ = "0.2.9"

__author__ = "alexpdev"

__all__ = (
    "main",
    "Benencoder",
    "Bendecoder",
    "TorrentFile",
    "TorrentFileV2",
    "TorrentFileHybrid",
)
