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

import os
import sys

from torrentfile.feeder import Feeder
from torrentfile.metafile import TorrentFile
from torrentfile.utils import (Benencoder, get_file_list, get_piece_length,
                               path_size, path_stat, Bendecoder)
from torrentfile.window import Application, Window, start
from torrentfile.torrentfile import cli_parse, CLI, main

__version__ = "1.2.1"
__author__ = "alexpdev"
__cwd__ = os.getcwd()
__platform__ = sys.platform

__all__ = [
    "__version__",
    "Application",
    "Benencoder",
    "Bendecoder",
    "Feeder",
    "TorrentFile",
    "Window",
    "cli_parse",
    "get_file_list",
    "get_piece_length",
    "main",
    "path_stat",
    "path_size",
    "start",
]
