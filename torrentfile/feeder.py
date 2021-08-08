import math
import os
from hashlib import sha256, sha1
from torrentfile.utils import path_size


class Feeder:
    def __init__(self, paths, piece_length, total_size=None, sha256=True):
        self.piece_length = piece_length
        self.paths = paths
        self.sha256 = sha256
        self.total_size = total_size
        self.pieces = []
        self.index = 0
        self.current = None
        self.generator = self.leaves()

    @property
    def total_pieces(self):
        if not self.total_size:
            self.total_size = sum(path_size(i) for i in self.paths)
        return math.ceil(self.total_size // self.piece_length)

    def hasher(self, data):
        if self.sha256:
            return sha256(data).digest()
        return sha1(data).digest()

    def __iter__(self):
        self.generator = self.leaves()
        return self.generator

    def __next__(self):
        return next(self.generator)

    def handle_partial(self, arr, partial):
        while partial < self.piece_length:
            temp = bytearray(self.piece_length - partial)
            size = self.current.readinto(temp)
            arr[partial : partial + size] = temp[:size]
            partial += size
            if partial < self.piece_length:
                if not self.next_file():
                    return self.hasher(arr[:partial])
        assert partial == self.piece_length
        return self.hasher(arr)

    def next_file(self):
        self.index += 1
        if self.index < len(self.paths):
            self.current.close()
            self.current = open(self.paths[self.index], "rb")
            return True
        return False

    def leaves(self):
        self.current = open(self.paths[self.index], "rb")
        while True:
            piece = bytearray(self.piece_length)
            size = self.current.readinto(piece)
            if size == 0:
                if not self.next_file():
                    break
            elif size < self.piece_length:
                yield self.handle_partial(piece, size)
            else:
                yield self.hasher(piece)
