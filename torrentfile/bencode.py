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

import re
import json

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


class BendecodingError:
    """Error occured during decode process."""
    pass


class BenencodingError:
    """Error occured during encoding process."""
    pass


class Bendecoder:
    """Decode class contains all decode methods."""

    def __init__(self, data=None):
        """
        Initialize instance with optional pre compiled data.

        Args:
            data (bytes-like, optional): target data for decoding.
        """
        self.data = data

    def tojson(self, bits=None):
        data, feed = self.decode(bits=bits)
        return json.dumps(data)


    def decode(self, bits=None):
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
            match, rest = self.decode(bits[feed:])
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
        match = re.match(b"(\d+):", bits)
        word_len, start = int(match.groups()[0]), match.span()[1]
        word = bits[start : start + word_len]
        try:
            word = word.decode("utf-8")
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
        obj = re.match(b"i(-?\d+)e", bits)
        return int(obj.group(1)), obj.end()


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


def bendecode_str(bits):
    """
    Bendecode string types.

    Args:
        bits (bytes): bencoded string

    Returns:
        str: Decoded data string
    """
    match = re.match(b"(\d+):", bits)
    word_len, start = int(match.groups()[0]), match.span()[1]
    word = bits[start : start + word_len]
    try:
        word = word.decode("utf-8")
    except:
        word = word.hex()
    return word, start + word_len


def bendecode_int(bits):
    """
    Decode intiger.

    Args:
        bits (bytes): becoded intiger bytes

    Returns:
        int: decoded int value
    """
    obj = re.match(b"i(-?\d+)e", bits)
    return int(obj.group(1)), obj.end()


def bendecode_dict(bits):
    """
    Decode dictionary.

    Args:
        bits (bytes): bencoded dictionary

    Returns:
        [dict]: decoded dictionary and contents
    """
    dic, feed = {}, 1
    while not bits[feed:].startswith(b"e"):
        match1, rest = bendecode(bits[feed:])
        feed += rest
        match2, rest = bendecode(bits[feed:])
        feed += rest
        dic[match1] = match2
    feed += 1
    return dic, feed


def bendecode_list(bits):
    """
    Decode list.

    Args:
        bits (bytes): bencoded list.

    Returns:
        list: decoded list and contents.
    """
    lst, feed = [], 1
    while not bits[feed:].startswith(b"e"):
        match, rest = bendecode(bits[feed:])
        lst.append(match)
        feed += rest
    feed += 1
    return lst, feed


def bendecode(bits):
    """
    Decode bencoded data.

    Args:
        bits (bytes): becoded data.

    Raises:
        Exception: Malformed data.

    Returns:
        any: decoded data.
    """
    if bits.startswith(b"i"):
        match, feed = bendecode_int(bits)
        return match, feed
    elif chr(bits[0]).isdigit():
        match, feed = bendecode_str(bits)
        return match, feed
    elif bits.startswith(b"l"):
        lst, feed = bendecode_list(bits)
        return lst, feed
    elif bits.startswith(b"d"):
        dic, feed = bendecode_dict(bits)
        return dic, feed
    else:
        raise BendecodingError


def benencode(val):
    """
    Encode data with bencoding.

    Args:
        val (any): Data.

    Raises:
        Exception: BenencodingError.

    Returns:
        bytes: Bencoded data.
    """
    if type(val) == str:
        return bencode_str(val)
    elif type(val) == int:
        return bencode_int(val)
    elif type(val) == list:
        return bencode_list(val)
    elif type(val) == dict:
        return bencode_dict(val)
    elif hasattr(val, "hex"):
        return bencode_bits(val)
    else:
        raise BenencodingError


def bencode_bits(bits):
    """
    Bencode bytes.

    Args:
        bits (bytes or bytearray): string

    Returns:
        bytes: bencoded string
    """
    size = str(len(bits)) + ":"
    return size.encode("utf-8") + bits


def bencode_str(txt):
    """
    Bencode string types.

    Args:
        txt (str): string

    Returns:
        bytes: bencoded string
    """
    size = str(len(txt)) + ":"
    return size.encode("utf-8") + txt.encode("utf-8")


def bencode_int(i):
    """
    Bencode integer type.

    Args:
        i (int): intiger

    Returns:
        bytes: bencoded int
    """
    return ("i" + str(i) + "e").encode("utf-8")


def bencode_list(elems):
    """
    Bencode list and contents.

    Args:
        elems (list): list of items for bencoding

    Returns:
        bytes: bencoded list and contents
    """
    arr = bytearray("l", encoding="utf-8")
    for elem in elems:
        encoded = benencode(elem)
        arr.extend(encoded)
    arr.extend(b"e")
    return arr


def bencode_dict(dic):
    """
    Bencode dictionary and contents.

    Args:
        dic (dict): key,value pairs of items for bencoding.

    Returns:
        bytes: Bencoded key, value pairs of data.
    """
    result = b"d"
    for k, v in dic.items():
        result += b"".join([benencode(k), benencode(v)])
    return result + b"e"
