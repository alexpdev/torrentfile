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

from torrentfile import utils, metafile, metafileV2, torrentfile, exceptions
from torrentfile.metafile import TorrentFile
from torrentfile.metafileV2 import TorrentFileV2
from torrentfile.torrentfile import main
from torrentfile.utils import path_stat, path_size

__version__ = "0.2.1"
__author__ = "alexpdev"

__all__ = [
    "metafile",
    "metafileV2",
    "torrentfile",
    "exceptions",
    "main",
    "path_stat",
    "path_size",
    "TorrentFile",
    "TorrentFileV2",
    "utils",
]
