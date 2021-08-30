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

from torrentfile import metafile, metafileV2, utils
from torrentfile.feeder import Feeder
from torrentfile.metafile import TorrentFile, Checker
from torrentfile.metafileV2 import TorrentFileV2
from torrentfile.torrentfile import CLI, Parser, main
from torrentfile.utils import (
    Bendecoder,
    Benencoder,
    get_file_list,
    get_piece_length,
    path_size,
    path_stat,
)

__version__ = "0.1.7"
__author__ = "alexpdev"

__all__ = [
    "__version__",
    "Bendecoder",
    "Benencoder",
    "Checker",
    "CLI",
    "Feeder",
    "Parser",
    "TorrentFile",
    "TorrentFileV2",
    "get_file_list",
    "get_piece_length",
    "main",
    "metafile",
    "metafileV2",
    "path_stat",
    "path_size",
    "utils",
]
