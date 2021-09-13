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
import json
import os
import re

from torrentfile.exceptions import BendecodingError, BenencodingError


class Bendecoder:
    """`Bendecoder` class contains all decode and convenience methods"""

    def __init__(self, data=None):
        """
        Initialize instance with optional pre compiled data.

        Args:

            * data (bytes-like, optional): target data for decoding.
        """
        self.data = data

    def tojson(self, bits=None):
        data, _ = self.decode(bits=bits)
        return json.dumps(data)

    def decode(self, bits=None):
        if bits is None:
            bits = self.data
        data, _ = self._decode(bits)
        return data

    def _decode(self, bits):
        """Decode bencoded data.

        args:
            bits (bytes): bencoded data for decoding.

        returns:
            any: the decoded data.
        """
        if bits is None:
            bits = self.data
        if bits.startswith(b"i"):
            match, feed = self._decode_int(bits)
            return match, feed

        # decode string
        elif chr(bits[0]).isdigit():
            num, feed = self._decode_str(bits)
            return num, feed

        # decode list and contents
        elif bits.startswith(b"l"):
            lst, feed = self._decode_list(bits)
            return lst, feed

        # decode dictionary and contents
        elif bits.startswith(b"d"):
            dic, feed = self._decode_dict(bits)
            return dic, feed
        else:
            raise BendecodingError

    def _decode_dict(self, bits):
        """
        Decode keys and values in dictionary.

        Args:
            bits (bytearray): bytes of data for decoding.

        Returns:
            [dict]: dictionary and contents.
        """
        dic, feed = {}, 1
        while not bits[feed:].startswith(b"e"):
            match1, rest = self.decode(bits[feed:])
            feed += rest
            match2, rest = self.decode(bits[feed:])
            feed += rest
            dic[match1] = match2
        feed += 1
        return dic, feed

    def _decode_list(self, bits):
        """
        Decode list and its contents.

        Args:
            bits (bytearray): bencoded data.

        Returns:
            [list]: decoded list and contents
        """
        lst, feed = [], 1
        while not bits[feed:].startswith(b"e"):
            match, rest = self._decode(bits[feed:])
            lst.append(match)
            feed += rest
        feed += 1
        return lst, feed

    def _decode_str(self, bits):
        """
        Decode string.

        Args:
            bits (bytearray): bencoded string.

        Returns:
            [str]: decoded string.
        """
        match = re.match(rb"(\d+):", bits)
        word_len, start = int(match.groups()[0]), match.span()[1]
        word = bits[start : start + word_len]
        try:
            word = word._decode("utf-8")
        except:
            word = word.hex()
        return word, start + word_len

    def _decode_int(self, bits):
        """
        Decode intiger.

        Args:
            bits (bytearray): bencoded intiger.

        Returns:
            [int]: decoded intiger.
        """
        obj = re.match(rb"i(-?\d+)e", bits)
        return int(obj.group(1)), obj.end()


class Benencoder:
    """Encode collection of methods for Bencoding data."""

    def __init__(self, data=None):
        """*__init__* Initialize Benencoder insance with optional pre compiled data.

        Args:

            * data (any, optional): Target data for encoding. Defaults to None.
        """
        self.data = data

    def encode(self, val=None):
        """*encode* Encode data with bencode protocol.

        args:

            * `bits` (bytes): bencoded data for decoding.

        returns:

            * `any`: the decoded data.
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

        elif type(val) == bool:
            return 1 if val else 0

        raise BenencodingError(val)

    def _encode_bytes(self, val):
        size = str(len(val)) + ":"
        return size.encode("utf-8") + val

    def _encode_str(self, txt):
        """Decode string.

        Args:

           * txt (str): string.

        Returns:

           * bytes: bencoded string.
        """
        size = str(len(txt)).encode("utf-8")
        return size + b":" + txt.encode("utf-8")

    def _encode_int(self, i):
        """Encode intiger.

        Args:

           * i (int): intiger.

        Returns:

            * bytes: bencoded intiger.
        """
        return b"i" + str(i).encode("utf-8") + b"e"

    def _encode_list(self, elems):
        """Encode list and its contents.

        Args:

           * elems (list): List of content to be encoded.

        Returns:

            * bytes: bencoded data
        """
        lst = [b"l"]
        for elem in elems:
            encoded = self.encode(elem)
            lst.append(encoded)
        lst.append(b"e")
        bit_lst = b"".join(lst)
        return bit_lst

    def _encode_dict(self, dic):
        """Encode keys and values in dictionary.

        Args:

            * dic (dict): dictionary of data for encoding.

        Returns:

            * bytes: bencoded data.
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


def get_piece_length(size):
    """
    Calculate the ideal piece length for bittorrent data.

    Args:

        * size (int): total bits of all files incluided in .torrent file.

    Returns:

        * int: the ideal peace length calculated from the size arguement.
    """
    exp = 14
    while size / (2 ** exp) > 50 and exp < 20:
        exp += 1
    if exp == 20 and size / MIB > 2000:
        pieces = lambda x: size / 2 ** x
        while 20 < pieces(exp) > 2000 and exp <= 23:
            exp += 1
    return 2 ** exp


def sortfiles(path):
    """*sortfiles* Generator function to sort and return files one at a time.

    Args:

        * path (path-like): directory path to get file list from.

    Yields:

        * path-like: next path in filelist
    """
    filelist = sorted(os.listdir(path), key=str.lower)
    for item in filelist:
        yield (item, os.path.join(path, item))


def _dir_files_sizes(path):
    """
    dir_files_sizes generates a file list and their sizes for given dir.

    Args:

        * path (path-like): directory to start FROM

    Returns:

        * tuple: filelist and total size.
    """
    if os.path.isfile(path):
        return [path], os.path.getsize(path)
    filelist, total = [], 0
    if os.path.isdir(path):
        for _, item in sortfiles(path):
            files, size = _dir_files_sizes(item)
            filelist.extend(files)
            total += size
    return filelist, total


def path_size(path):
    """Calculate sum of all filesizes within directory.

    Args:

        * path (pathlike): The path to start calculating from.

    Returns:

        * int: total sum in bytes
    """
    size = 0
    if os.path.isfile(path):
        return os.path.getsize(path)

    # recursive sum for all files in folder
    elif os.path.isdir(path):
        for name in os.listdir(path):
            fullpath = os.path.join(path, name)
            size += path_size(fullpath)
    return size


def get_file_list(path, sort=False):
    """Search directory tree for files.

    Args:

        * path (pathlike): path to file or directory base
        * sort (bool, optional): return list sorted. Defaults to False.

    Returns:

        * list: all file paths within directory tree.
    """
    if os.path.isfile(path):
        return [path]

    # put all files into filelist within directory
    files = list()
    filelist = os.listdir(path)

    # optional canonical sort of filelist
    if sort:
        filelist.sort(key=str.lower)

    # recursive for all folders
    for item in filelist:
        full = os.path.join(path, item)
        files.extend(get_file_list(full, sort=sort))
    return files


def path_stat(path):
    """combines a series of functions to work like a stat call for a directory and its contents."""
    filelist, size = _dir_files_sizes(path)
    piece_length = get_piece_length(size)
    return (filelist, size, piece_length)


def path_piece_length(path):
    psize = path_size(path)
    return get_piece_length(psize)
