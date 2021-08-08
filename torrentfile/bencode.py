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
