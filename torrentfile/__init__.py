#! /usr/bin/python3
# -*- coding: utf-8 -*-

#####################################################################
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#####################################################################

from torrentfile.feeder import Feeder
from torrentfile.metafile import TorrentFile
from torrentfile.utils import (
    path_stat,
    get_piece_length,
    get_file_list,
    path_size,
    Benencoder,
)

__version__ = "1.1.0"
__author__ = "alexpdev"

__all__ = [
    "TorrentFile",
    "get_piece_length",
    "path_size",
    "folder_stat",
    "Benencoder",
    "Feeder",
    "path_stat",
    "get_file_list",
]
