import os
import hashlib
from pathlib import Path
from torrentfile.piecelength import get_piece_length
from torrentfile.utils import md5, sha1

class PieceHasher:
    def __init__(self, path, piece_length=None, usemd5=False):
        self.path = path
        self.usemd5 = usemd5
        self.Path = Path(path)
        self.name = self.Path.name
        self.piece_length = piece_length
        self.files = []
        self.paths = []
        self.pieces = []
        self.size = 0
        if os.path.isfile(path):
            self.length = os.path.getsize(path)
            if not self.piece_length:
                self.piece_length = get_piece_length(self.length)
        else:
            self.walk_path(self.Path, self.path)
            if not self.piece_length:
                self.piece_length = get_piece_length(self.size)

    def walk_path(self, path, root):
        listdir = sorted(os.listdir(path),key=str.lower)
        for item in listdir:
            full_path = os.path.join(path,item)
            if os.path.isdir(full_path):
                self.walk_path(full_path, root)
            else:
                self.paths.append(full_path)
                size = os.path.getsize(full_path)
                self.size += size
                parts = os.path.relpath(full_path, root).split(os.sep)
                fdict = {"length": size, "path": parts}
                if self.usemd5:
                    fdict["md5sum"] = md5(open(full_path,"rb").read()).digest()
                self.files.append(fdict)
        return

    def single_file_hash(self):
        pieces = bytearray()
        with open(self.path,"rb") as filename:
            piece = bytearray(self.piece_length)
            while True:
                size = filename.readinto(piece)
                if size == self.piece_length:
                    digest = sha1(piece)
                    pieces.extend(digest)
                elif size == 0:
                    break
                elif size < self.piece_length:
                    digest = sha1(piece[:size])
                    pieces.extend(digest)
        self.pieces = pieces
        return self.pieces

    def _concat(self):
        arr = bytearray()
        for path in self.paths:
            arr.extend(open(path,"rb").read())
            self.gen_pieces(arr)
        self.gen_pieces(arr,last=True)
        return self.pieces

    def gen_pieces(self, arr, last=False):
        while len(arr) >= self.piece_length:
            self.pieces.append(sha1(arr[:self.piece_length - 1]))
            del arr[:self.piece_length-1]
        if last:
            self.pieces.append(sha1(arr))
            del arr
        return

    def get_pieces(self):
        if os.path.isfile(self.path):
            return self.single_file_hash()
        return self._concat()
