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

"""Utility functions and classes used throughout package.

Functions:
  get_piece_length: calculate ideal piece length for torrent file.
  sortfiles: traverse directory in sorted order yielding paths encountered.
  path_size: Sum the sizes of each file in path.
  get_file_list: Return list of all files contained in directory.
  path_stat: Get ideal piece length, total size, and file list for directory.
  path_piece_length: Get ideal piece length based on size of directory.
"""

import os
from datetime import datetime

from . import __version__ as version


class MissingPathError(Exception):
    """Path parameter is required to specify target content.

    Creating a .torrent file with no contents seems rather silly.

    Args:
      message (`any`, optional): Value cannot be interpreted by decoder.
    """

    def __init__(self, message=None):
        """Raise when creating a meta file without specifying target content.

        The `message` argument is a message to pass to Exception base class.
        """
        self.message = f"Path arguement is missing and required {str(message)}"
        super().__init__(message)


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

    def __init__(self, path=None, announce=None, announce_list=None,
                 private=False, source=None, piece_length=None,
                 comment=None, outfile=None):
        """Construct MetaFile superclass and assign local attributes.

        Keyword parameters include path, announce, announce_list private,
        source, piece_length, comment, outfile.
        """
        if not path:
            raise MissingPathError
        # base path to torrent content.
        self.path = path
        # Format piece_length attribute.
        if not piece_length:
            piece_length = path_piece_length(self.path)
        elif isinstance(piece_length, str):
            piece_length = int(piece_length)
        # Coming from CLI is most likely a string.
        if 13 < piece_length < 36:
            # Under 36 means its used as exponent to 2**n.
            piece_length = 2 ** piece_length
            # Otherwise just cast to integer.
        self.piece_length = piece_length
        # Assign announce URL to empty string if none provided.
        if not announce:
            announce = ""
        # Most torrent clients have editting trackers as a feature.
        self.announce = announce
        self.announce_list = announce_list
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

    def write(self, outfile=None):
        """Overload when subclassed.

        Raises:
            NotImplementedError (`Exception`)
        """
        raise NotImplementedError


def get_piece_length(size):
    """Calculate the ideal piece length for bittorrent data.

    Args:
      size (`int`): Total bits of all files incluided in .torrent file.

    Returns:
      (`int`): Ideal peace length calculated from the size arguement.
    """
    exp = 14
    while size / (2 ** exp) > 200 and exp < 23:
        exp += 1
    return 2 ** exp


def sortfiles(path):
    """Sort entries in path.

    Args:
        path (`str`): Target directory for sorting contents.

    Returns:
        (`iterator`): yield sorted content.
    """
    items = sorted(os.listdir(path), key=str.lower)
    for item in items:
        full = os.path.join(path, item)
        yield item, full


def filelist_total(path):
    """Search directory tree for files.

    Args:
      path (`str`): Path to file or directory base
      sort (`bool`): Return list sorted. Defaults to False.

    Returns:
      (`list`): All file paths within directory tree.
    """
    if os.path.isfile(path):
        file_size = os.path.getsize(path)
        return file_size, [path]

    # put all files into filelist within directory
    files = []
    total_size = 0
    filelist = sorted(os.listdir(path), key=str.lower)

    for name in filelist:
        full = os.path.join(path, name)

        size, paths = filelist_total(full)

        total_size += size
        files.extend(paths)
    return total_size, files


def path_size(path):
    """Return the total size of all files in path recursively.

    Args:
        path (`str`): path to target file or directory.

    Returns:
        size (`int`): total size of files.
    """
    total_size, _ = filelist_total(path)
    return total_size


def get_file_list(path):
    """Return a sorted list of file paths contained in directory.

    Args:
        path (`str`): target file or directory.

    Returns:
        filelist (`list`): sorted list of file paths.
    """
    _, filelist = filelist_total(path)
    return filelist


def path_stat(path):
    """Calculate directory statistics.

    Args:
        path (`str`): The path to start calculating from.

    Returns:
        filelist (`list`):  List of all files contained in Directory
        size (`int`): Total sum of bytes from all contents of dir
        piece_length (`int`): The size of pieces of the torrent contents.
    """
    total_size, filelist = filelist_total(path)
    piece_length = get_piece_length(total_size)
    return (filelist, total_size, piece_length)


def path_piece_length(path):
    """Calculate piece length for input path and contents.

    Args:
      path (`str`): The absolute path to directory and contents.

    Returns:
      piece_length (`int`): The size of pieces of torrent content.
    """
    psize = path_size(path)
    return get_piece_length(psize)
