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
"""Module for the Base class for other MetaFile classes throughout package.

Classes:
    MetaFile (`obj`): base class for all MetaFile classes.
"""

from collections.abc import Sequence
from datetime import datetime

import pyben

from . import utils
from .version import __version__ as version


class MetaFile:
    """Base Class for all TorrentFile classes.

    Args:
        path (`str`): target path to torrent content.
        announce (`str`): Tracker URL.
        announce_list (`list`): Additional tracker URL's.
        comment (`str`): A comment.
        piece_length (`int`): Size of torrent pieces.
        private (`bool`): For private trackers?
        outfile (`str`): target path to write .torrent file.
        source (`str`): Private tracker source.
    """

    def __init__(self, path=None, announce=None, private=False,
                 source=None, piece_length=None, comment=None, outfile=None):
        """Construct MetaFile superclass and assign local attributes.

        Keyword parameters include path, announce, announce_list private,
        source, piece_length, comment, outfile.
        """
        if not path:
            raise utils.MissingPathError

        # base path to torrent content.
        self.path = path

        # Format piece_length attribute.
        if piece_length:
            self.piece_length = utils.normalize_piece_length(piece_length)
        else:
            self.piece_length = utils.path_piece_length(self.path)
        # Assign announce URL to empty string if none provided.
        self.announce_list = None
        if not announce:
            self.announce = ""
        # Most torrent clients have editting trackers as a feature.
        elif isinstance(announce, str):
            self.announce = announce
        elif isinstance(announce, Sequence):
            self.announce = announce[0]
            # if announce has more than 1 argumnt
            if len(announce) > 1:
                # all but the first go to announce list field
                self.announce_list = announce[1:]

        if private:
            self.private = 1
        else:
            self.private = private

        self.source = source
        self.comment = comment
        self.outfile = outfile

    def apply_constants(self):
        """Apply values to meta dict that are input independent.

        Args:
            meta (`dict`,default=`None`): Meta dictionary.

        Returns:
            meta (`dict`): Filled meta dictionary.
        """
        return {
            "announce": self.announce,
            "created by": f"TorrentFile:v{version}",
            "creation date": int(datetime.timestamp(datetime.now()))
        }

    def assemble(self):
        """Overload in subclasses.

        Raises:
            NotImplementedError (`Exception`)
        """
        raise NotImplementedError

    def sort_meta(self):
        """Sort the info and meta dictionaries."""
        meta = self.meta
        meta["info"] = dict(sorted(list(meta["info"].items())))
        meta = dict(sorted(list(meta.items())))
        return meta

    def write(self, outfile=None):
        """Write meta information to .torrent file.

        Args:
            outfile (`str`, default=None): Destination path for .torrent file.

        Returns:
            outfile (`str`): Where the .torrent file was writen.
            meta (`dict`): .torrent meta information.
        """
        if outfile is not None:
            self.outfile = outfile

        if self.outfile is None:
            self.outfile = self.path + ".torrent"

        self.meta = self.sort_meta()
        pyben.dump(self.meta, self.outfile)
        return self.outfile, self.meta
