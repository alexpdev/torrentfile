#! /usr/bin/python3
# -*- coding: utf-8 -*-


import re

"""Collection of functions and classes for encoding and decoding with bencoded data"""

class Bendecoder:
    """Decode class contains all decode methods."""

    def decode(self, bits):
        """Decode bencoded data.

        args:
            bits (bytes): bencoded data for decoding.

        returns:
            any: the decoded data.
        """
        if bits.startswith(b"i"):
            match, feed = self.de_int(bits)
            return match, feed

        # decode string
        elif chr(bits[0]).isdigit():
            match, feed = self.de_str(bits)
            return match, feed

        # decode list and contents
        elif bits.startswith(b"l"):
            lst, feed = self.de_list(bits)
            return lst, feed

        # decode dictionary and contents
        elif bits.startswith(b"d"):
            dic, feed = self.de_dict(bits)
            return dic, feed
        else:
            raise Exception

    def de_dict(self, bits):
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

    def de_list(self, bits):
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

    def de_str(self, bits):
        """
        Decode string.

        Args:
            bits (bytearray): bencoded string.

        Returns:
            [str]: decoded string.
        """
        match = re.match(b"(\\d+):", bits)
        word_len, start = int(match.groups()[0]), match.span()[1]
        word = bits[start: start + word_len]
        try:
            word = word.decode("utf-8")
        except:
            word = word
        return word, start + word_len

    def de_int(self, bits):
        """
        Decode intiger.

        Args:
            bits (bytearray): bencoded intiger.

        Returns:
            [int]: decoded intiger.
        """
        obj = re.match(b"i(-?\\d+)e", bits)
        return int(obj.group(1)), obj.end()


class Benencoder:
    """Encode collection of methods for Bencoding data."""

    def encode(self, val):
        """Encode data with bencode protocol.

        args:
            bits (bytes): bencoded data for decoding.

        returns:
            any: the decoded data.
        """
        if type(val) == str:
            return self.to_str(val)
        elif type(val) == int:
            return self.to_int(val)
        elif type(val) == list:
            return self.to_list(val)
        elif type(val) == dict:
            return self.to_dict(val)
        else:
            return

    def to_str(self, txt):
        """
        Decode string.

        Args:
            txt (str): string.

        Returns:
            [bytes]: bencoded string.
        """
        size = str(len(txt))
        return size.encode("utf-8") + b":" + txt.encode("utf-8")

    def to_int(self, i):
        """
        Encode intiger.

        Args:
            i (int): intiger.

        Returns:
            [bytes]: bencoded intiger.
        """
        return b"i" + bytes(str(i)) + b"e"

    def to_list(self, elems):
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

    def to_dict(self, dic):
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


def de_str(bits):
    """
    Bendecode string types.

    Args:
        bits (bytes): bencoded string

    Returns:
        str: Decoded data string
    """
    match = re.match(b"(\\d+):",bits)
    word_len, start = int(match.groups()[0]), match.span()[1]
    word = bits[start : start + word_len]
    try:
        word = word.decode("utf-8")
    except:
        word = word.__repr__()
    return word, start + word_len


def de_int(bits):
    """
    Decode intiger.

    Args:
        bits (bytes): becoded intiger bytes

    Returns:
        int: decoded int value
    """
    obj = re.match(b"i(-?\d+)e", bits)
    return int(obj.group(1)), obj.end()


def de_dict(bits):
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

def de_list(bits):
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
        match, feed = de_int(bits)
        return match, feed
    elif chr(bits[0]).isdigit():
        match, feed = de_str(bits)
        return match,feed
    elif bits.startswith(b"l"):
        lst, feed = de_list(bits)
        return lst, feed
    elif bits.startswith(b"d"):
        dic, feed = de_dict(bits)
        return dic, feed
    else:
        raise Exception

def bencode(self,val):
    """
    Encode data with bencoding.

    Args:
        val (any): Data.

    Raises:
        Exception: Invalid type.

    Returns:
        bytes: Bencoded data.
    """
    if type(val) == str:
        return self.to_str(val)
    elif type(val) == int:
        return self.to_int(val)
    elif type(val) == list:
        return self.to_list(val)
    elif type(val) == dict:
        return self.to_dict(val)
    else:
        raise Exception

def to_str(txt):
    """
    Bencode string types.

    Args:
        txt (str): string

    Returns:
        bytes: bencoded string
    """
    size = str(len(txt)).encode("utf-8")
    return size + b":" + txt.encode("utf-8")

def to_int(i):
    """
    Bencode integer type.

    Args:
        i (int): intiger

    Returns:
        bytes: bencoded int
    """
    return b"i" + b"{i}" + b"e"

def to_list(elems):
    """
    Bencode list and contents.

    Args:
        elems (list): list of items for bencoding

    Returns:
        bytes: bencoded list and contents
    """
    lst = [b"l"]
    for elem in elems:
        encoded = bencode(elem)
        lst.append(encoded)
    lst.append(b"e")
    bit_lst = b"".join(lst)
    return bit_lst

def to_dict(dic):
    """
    Bencode dictionary and contents.

    Args:
        dic (dict): key,value pairs of items for bencoding.

    Returns:
        bytes: Bencoded key, value pairs of data.
    """
    result = b"d"
    for k,v in dic.items():
        result += b"".join([bencode(k), bencode(v)])
    return result + b"e"
