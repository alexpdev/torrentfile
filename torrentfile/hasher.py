import os
import hashlib
from pathlib import Path
from torrentfile.piecelength import get_piece_length

def sha1(data):
    piece = hashlib.sha1()
    piece.update(data)
    return piece.digest()

def sha256(data):
    piece = hashlib.sha256()
    piece.update(data)
    return piece.digest()

def md5(data):
    piece = hashlib.md5()
    piece.update(data)
    return piece.digest()

class PieceHasher:
    def __init__(self, path, piece_length=None, usemd5=False):
        self.path = path
        self.usemd5 = usemd5
        self.Path = Path(path)
        self.name = self.Path.name
        self.piece_length = piece_length
        self.files = []
        self.paths = []
        self.pieces = None
        self.size = 0
        if os.path.isfile(path):
            self.length = os.path.getsize(path)
            if not self.piece_length:
                self.piece_length = get_piece_length(self.length)
        else:
            self.walk_path(self.Path, self.path)

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
                parts = [str(i).encode("utf-8") for i in parts]
                fdict = {"length": size, "path": parts}
                if self.usemd5:
                    fdict["md5sum"] = md5(open(full_path,"rb").read()).digest()
                self.files.append(fdict)
        return

    def single_file_hash(self):
        pieces = []
        with open(self.path,"rb") as filename:
            piece = bytearray(self.piece_length)
            while True:
                size = filename.readinto(piece)
                if size == self.piece_length:
                    digest = sha1(piece)
                    pieces.append(digest)
                elif size == 0:
                    break
                elif size < self.piece_length:
                    digest = sha1(piece[:size])
                    pieces.append(digest)
        self.pieces = ''.join(pieces)
        return self.pieces


    def get_pieces(self):
        if os.path.isfile(self.path):
            return self.single_file_hash()
        if not self.piece_length:
            self.piece_length = get_piece_length(self.size)
        pieces = list()
        if not self.paths:
            self.walk_path(self.path)
        for filename in self.paths:
            data = bytearray(self.piece_length)
            with open(filename,"rb") as fd:
                while True:
                    size = fd.readinto(data)
                    if size == self.piece_length:
                        pieces.append(sha1(data))
                    elif size == 0:
                        break
                    elif size < self.piece_length:
                        pieces.append(sha1(data[:size]))
        self.pieces = b''.join(pieces)
        return self.pieces
