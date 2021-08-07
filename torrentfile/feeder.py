import math
import os
from torrentfile.utils import sha1, sha256, path_size

class Feeder:

    def __init__(self, paths, piece_length, total_size=None, sha256=True):
        self.piece_length = piece_length
        self.paths = paths
        self.sha256 = sha256
        self.total_size = total_size
        self.pieces = []
        self._partial = 0
        self.index = 0
        self.current = None
        self._generator = None

    @property
    def total_pieces(self):
        if not self.total_size:
            self.total_size = sum(path_size(i) for i in self.paths)
        return math.ceil(self.total_size // self.piece_length)

    @property
    def hasher(self):
        if self.sha256:
            return sha256
        return sha1

    def __iter__(self):
        self._generator = self.leaves()
        return self._generator

    def __next__(self):
        return next(self._generator)

    def _handle_partial(self, arr):
        part_size = self.partial
        temp = bytearray(self.piece_length - part_size)
        self.current.readinto(temp)
        arr[part_size:] = temp
        assert temp == arr[part_size:]
        assert len(arr) == self.piece_length
        self.reset_partial()
        return self.hasher(part_size)

    def _next_path(self):
        self.current.close()
        self.index += 1

    @property
    def partial(self):
        return self._partial

    def set_partial(self, number):
        self._partial = number

    def reset_partial(self):
        self._partial = 0

    def leaves(self):
        counter = 0
        piece = bytearray(self.piece_length)
        while self.index < len(self.filenames):
            self.current = open(self.filenames[self.index],"rb")
            if self.partial:
                yield self._handle_partial(piece)
                counter += 1
            while True:
                size = self.current.readinto(piece)
                if size == 0: break
                elif size < self.piece_length:
                    self.set_partial(size)
                    break
                yield self.hasher(piece)
                counter += 1
            self._next_path()
        if self.partial: yield sha1(piece[:self.partial])
