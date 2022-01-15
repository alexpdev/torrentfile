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

import math
import os
from pathlib import Path


class MissingPathError(Exception):
    """Path parameter is required to specify target content.

    Creating a .torrent file with no contents seems rather silly.

    Parameters
    ----------
    message : `any`
        Message for user (optional).
    """

    def __init__(self, message=None):
        """Raise when creating a meta file without specifying target content.

        The `message` argument is a message to pass to Exception base class.
        """
        self.message = f"Path arguement is missing and required {str(message)}"
        super().__init__(message)


class PieceLengthValueError(Exception):
    """Piece Length parameter must equal a perfect power of 2.

    Parameters
    ----------
    message : `any`
        Message for user (optional).
    """

    def __init__(self, message=None):
        """Raise when creating a meta file with incorrect piece length value.

        The `message` argument is a message to pass to Exception base class.
        """
        self.message = f"Incorrect value for piece length: {str(message)}"
        super().__init__(message)


def humanize_bytes(amount):
    """Convert integer into human readable memory sized denomination.

    Parameters
    ----------
    amount : `int`
        total number of bytes.

    Returns
    -------
    `str` :
        human readable representation of the given amount of bytes.
    """
    if amount < 1024:
        return str(amount)
    if 1024 <= amount < 1_048_576:
        return f"{amount // 1024} KiB"
    if 1_048_576 <= amount < 1_073_741_824:
        return f"{amount // 1_048_576} MiB"
    return f"{amount // 1073741824} GiB"


def normalize_piece_length(piece_length) -> int:
    """Verify input piece_length is valid and convert accordingly.

    Parameters
    ----------
    piece_length : `int` | `str`
        The piece length provided by user.

    Returns
    -------
    piece_length : `int`
        normalized piece length.

    Raises
    ------
    PieceLengthValueError :
        If piece length is improper value.
    """
    if isinstance(piece_length, str):
        if piece_length.isnumeric():
            piece_length = int(piece_length)
        else:
            raise PieceLengthValueError(piece_length)

    if 13 < piece_length < 26:
        return 2 ** piece_length
    if piece_length <= 13:
        raise PieceLengthValueError(piece_length)

    log = int(math.log2(piece_length))
    if 2 ** log == piece_length:
        return piece_length
    raise PieceLengthValueError


def get_piece_length(size: int) -> int:
    """Calculate the ideal piece length for bittorrent data.

    Parameters
    ----------
    size : `int`
        Total bits of all files incluided in .torrent file.

    Returns
    -------
    piece_length : `int`
        Ideal peace length size arguement.
    """
    exp = 14
    while size / (2 ** exp) > 200 and exp < 25:
        exp += 1
    return 2 ** exp


def filelist_total(pathstring):
    """Perform error checking and format conversion to os.PathLike.

    Parameters
    ----------
    pathstring : `str`
        An existing filesystem path.

    Returns
    -------
    `os.PathLike`
        Input path converted to bytes format.

    Raises
    ------
    MissingPathError
        File could not be found.
    """
    if os.path.exists(pathstring):
        path = Path(pathstring)
        return _filelist_total(path)
    raise MissingPathError


def _filelist_total(path):
    """Search directory tree for files.

    Parameters
    ----------
    path : `str`
        Path to file or directory base
    sort : `bool`
        Return list sorted. Defaults to False.

    Returns
    -------
    filelist : `list`
        All file paths within directory tree.
    total : `int`
        Sum of all filesizes in filelist.
    """
    if path.is_file():
        file_size = os.path.getsize(path)
        return file_size, [str(path)]
    total = 0
    filelist = []
    if path.is_dir():
        for item in path.iterdir():
            size, paths = filelist_total(item)
            total += size
            filelist.extend(paths)
    return total, sorted(filelist)


def path_size(path):
    """Return the total size of all files in path recursively.

    Parameters
    ----------
    path : `str`
        path to target file or directory.

    Returns
    -------
    size : `int`
        total size of files.
    """
    total_size, _ = filelist_total(path)
    return total_size


def get_file_list(path):
    """Return a sorted list of file paths contained in directory.

    Parameters
    ----------
    path : `str`
        target file or directory.

    Returns
    -------
    filelist : `list`
        sorted list of file paths.
    """
    _, filelist = filelist_total(path)
    return filelist


def path_stat(path):
    """Calculate directory statistics.

    Parameters
    ----------
    path : `str`
        The path to start calculating from.

    Returns
    -------
    filelist : `list`
        List of all files contained in Directory
    size : `int`
        Total sum of bytes from all contents of dir
    piece_length : `int`
        The size of pieces of the torrent contents.
    """
    total_size, filelist = filelist_total(path)
    piece_length = get_piece_length(total_size)
    return (filelist, total_size, piece_length)


def path_piece_length(path):
    """Calculate piece length for input path and contents.

    Parameters
    ----------
    path : `str`
        The absolute path to directory and contents.

    Returns
    -------
    piece_length : `int`
        The size of pieces of torrent content.
    """
    psize = path_size(path)
    return get_piece_length(psize)


def next_power_2(value):
    """Calculate the next perfect power of 2 equal to or greater than value.

    Parameters
    ----------
    value : `int`
        integer value that is less than some perfect power of 2.

    Returns
    -------
    `int`
        The next power of 2 greater than value, or value if already power of 2.
    """
    if not value & (value - 1) and value:
        return value
    start = 1
    while start < value:
        start <<= 1
    return start
