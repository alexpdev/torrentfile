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

import math
from hashlib import sha1


class Feeder:
    """Seemlesly generate hashes of piece length data from filelist contents."""

    def __init__(self, paths, piece_length, total):
        """
        __init__ Constructor for the Feeder class.

        Args:

            * paths (list[str]): list of files.
            * piece_length (int): Size of chuncks to split the data into.
            * total (int): Sum of all files in file list.
        """
        self.piece_length = piece_length
        self.paths = paths
        self.total = total
        self.pieces = []
        self.index = 0
        self.current = open(self.paths[self.index], "rb")
        self.iterator = self.leaves()

    def __iter__(self):
        """*__iter__* iterate through feed pieces.

        Returns:

            * iterator: Iterator object
        """
        self.iterator = self.leaves()
        return self.iterator

    def __next__(self):
        """*__next__* returns the next element from iterator.

        Returns:

            * bytes-like: piece_length length pieces of data.
        """
        return self.iterator.__next__()

    def total_pieces(self):
        """*total_pieces* total size / piece length.

        Returns:

            * int: number of pieces for entire torrrent
        """
        return math.ceil(self.total // self.piece_length)

    def handle_partial(self, arr, partial):
        """
        handle_partial seemlessly move to next file for input data.

        Args:

            * arr (bytes-like): incomplete piece containing partial data
            * partial (int): size of incomplete piece_length

        Returns:

            * bytes-like: final piece filled with data.
        """
        while partial < self.piece_length:
            temp = bytearray(self.piece_length - partial)
            size = self.current.readinto(temp)
            arr[partial : partial + size] = temp[:size]
            partial += size
            if partial < self.piece_length:
                if not self.next_file():
                    return sha1(arr[:partial]).digest()
        assert partial == self.piece_length
        return sha1(arr).digest()

    def next_file(self):
        """
        next_file Seemlessly transition to next file in file list.

        Returns:

            * bool: returns false if no more files are left
        """
        self.index += 1
        if self.index < len(self.paths):
            self.current.close()
            self.current = open(self.paths[self.index], "rb")
            return True
        return False

    def leaves(self):
        """
        leaves generator of piece-length pieces of data from input file list.

        Yields:

            * bytes: hash values of chuncked data.
        """
        while True:
            piece = bytearray(self.piece_length)
            size = self.current.readinto(piece)
            if size == 0:
                if not self.next_file():
                    self.current.close()
                    break
            elif size < self.piece_length:
                yield self.handle_partial(piece, size)
            else:
                yield sha1(piece).digest()
