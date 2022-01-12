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
"""
Torrentfile can create Bittorrent metafiles for any content.

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
import sys
import logging

from torrentfile import interactive, utils
from torrentfile.cli import main, main_script
from torrentfile.recheck import Checker
from torrentfile.torrent import TorrentFile, TorrentFileHybrid, TorrentFileV2
from torrentfile.version import __version__

__author__ = "alexpdev"
logger = logging.getLogger(__name__)

def setLogger(logger):
    """Initial setup for the application logging functionality.

    Parameters
    ----------
    logger : `logging.Logger`
        the logger class used throughout program.

    Returns
    -------
    handlers : `list`
        collection of handlers used by the logger class.
    """
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        fmt="%(asctime)s %(message)s",
        datefmt="%m/%d %H:%M:%S",
        style="%",
    )
    handlers =  [
        logging.StreamHandler(stream=sys.stdout),
        logging.FileHandler("torrentfile.log", mode="w", encoding="utf-8")
    ]
    for handle in handlers:
        handle.setFormatter(formatter)
        handle.setLevel(logging.WARNING)
        logger.addHandler(handle)
    return handlers

handlers = setLogger(logger)

def setLevel(level=logging.DEBUG):
    """Set the logging stream handler to provided level.

    Parameters
    ----------
    level : `int`
        The variable representation of #1-5.
    """
    for handle in handlers:
        handle.setLevel(level)
