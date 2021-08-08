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

"""
Library of functions and classes for encoding and decoding bencoded data.

Usage: How to import:

>> from benencoding import *
>> from benencoding import Benencoder, Bendecoder
>> from benencoding import benencode, bendecode

Usage: How to Encode/Decode:

>> data = b'l18:Some Bencoded Datai15ee'
>> decoder = Bendecoder(data)
>> decoder.decode()
['Some Bencoded Data', 15]
>> results = bendecode(data)
['Some Bencoded Data', 15]
>> encoder = Benencoder(results).encode()
b'l18:Some Bencoded Datai15ee'
>> benencode(results)
b'l18:Some Bencoded Datai15ee'
"""
import os
from pathlib import Path


class BenencodingError:
    """Error occured during encoding process."""

    pass


class Benencoder:
    """Encode collection of methods for Bencoding data."""

    def __init__(self, data=None):
        """Initialize Benencoder insance with optional pre compiled data.

        Args:
            data (any, optional): Target data for encoding. Defaults to None.
        """
        self.data = data

    def encode(self, val=None):
        """Encode data with bencode protocol.

        args:
            bits (bytes): bencoded data for decoding.

        returns:
            any: the decoded data.
        """
        if val is None:
            val = self.data
        if type(val) == str:
            return self._encode_str(val)

        if hasattr(val, "hex"):
            return self._encode_bytes(val)

        elif type(val) == int:
            return self._encode_int(val)

        elif type(val) == list:
            return self._encode_list(val)

        elif type(val) == dict:
            return self._encode_dict(val)

        raise BenencodingError

    def _encode_bytes(self, val):
        size = str(len(val)) + ":"
        return size.encode("utf-8") + val

    def _encode_str(self, txt):
        """
        Decode string.

        Args:
            txt (str): string.

        Returns:
            [bytes]: bencoded string.
        """
        size = str(len(txt)).encode("utf-8")
        return size + b":" + txt.encode("utf-8")

    def _encode_int(self, i):
        """
        Encode intiger.

        Args:
            i (int): intiger.

        Returns:
            [bytes]: bencoded intiger.
        """
        return b"i" + str(i).encode("utf-8") + b"e"

    def _encode_list(self, elems):
        """
        Encode list and its contents.

        Args:
            elems (list): List of content to be encoded.

        Returns:
            [bytes]: bencoded data
        """
        lst = [b"l"]
        for elem in elems:
            encoded = self.encode(elem)
            lst.append(encoded)
        lst.append(b"e")
        bit_lst = b"".join(lst)
        return bit_lst

    def _encode_dict(self, dic):
        """
        Encode keys and values in dictionary.

        Args:
            dic (dict): dictionary of data for encoding.

        Returns:
            [bytes]: bencoded data.
        """
        result = b"d"
        for k, v in dic.items():
            result += b"".join([self.encode(k), self.encode(v)])
        return result + b"e"


KIB = 1 << 10
MIB = KIB * KIB
GIB = KIB ** 3
MIN_BLOCK = 2 ** 14
TOP_SIZE = 2 ** 18

resolve = lambda x: Path(x).resolve()


def get_piece_length(size):
    """
    Calculate the ideal piece length for bittorrent data.

    Args:
        size (int): total bits of all files incluided in .torrent file

    Returns:
        int: the ideal peace length calculated from the size arguement
    """
    exp = 14
    while size / (2 ** exp) > 50 and exp < 20:
        exp += 1
    if exp == 19 and size / MIB > 2000:
        while size / (2 ** exp) > 2000 and exp <= 23:
            exp += 1
    return 2 ** exp


def sortfiles(path):
    filelist = sorted(os.listdir(path), key=str.lower)
    for item in filelist:
        yield os.path.join(path, item)


def dir_files_sizes(path):
    if os.path.isfile(path):
        return [path], os.path.getsize(path)
    filelist, total = [], 0
    if os.path.isdir(path):
        for item in sortfiles(path):
            files, size = dir_files_sizes(item)
            filelist.extend(files)
            total += size
    return filelist, total


def path_size(path):
    """Calculate sum of all filesizes within directory.

    Args:
        path (pathlike): The path to start calculating from.

    Returns:
        int: total sum in bytes
    """
    if os.path.isfile(path):
        return os.path.getsize(path)

    # recursive sum for all files in folder
    elif os.path.isdir(path):
        size = 0
        for name in os.listdir(path):
            fullpath = os.path.join(path, name)
            size += path_size(fullpath)
    return size


def get_file_list(path, sort=False):
    """Search directory tree for files.

    Args:
        path (pathlike): path to file or directory base
        sort (bool, optional): return list sorted. Defaults to False.

    Returns:
        [list]: all file paths within directory tree.
    """
    if os.path.isfile(path):
        return [path]

    # put all files into filelist within directory
    files = list()
    filelist = os.listdir()

    # optional canonical sort of filelist
    if sort:
        filelist.sort(key=str.lower)

    # recursive for all folders
    for item in filelist:
        full = os.path.join(path, item)
        files.extend(get_file_list(full, sort=sort))
    return files


def path_stat(path):
    filelist, size = dir_files_sizes(path)
    piece_length = get_piece_length(size)
    return (filelist, size, piece_length)


def do_something():
    pass
