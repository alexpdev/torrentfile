import os
import hashlib
from pathlib import Path
from torrentfile.piecelength import get_piece_length

inf = {
    "pieces": "",
    "piece length": 0,
    "files" : {},
    "name" : "",
}


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
    def __init__(self, path):
        self.path = path
        self.Path = Path(path)
        self.name = self.Path.name
        self.piece_length = None
        self.files = []
        self.paths = []
        self.pieces = None
        self.size = 0
        if os.path.isfile(path):
            self.length = os.path.getsize(path)
            self.piece_length = get_piece_length(self.length)
        else:
            self.walk_path(self.Path,self.name)

    def walk_path(self, path, root):
        listdir = sorted(os.listdir(path),key=str.lower)
        for item in listdir:
            p = os.path.join(path,item)
            self.paths.append(p)
            size = os.path.getsize(p)
            self.size += size
            full_path = os.path.join(path,item)
            parts = os.path.relpath(full_path, root).split(os.sep)[1:]
            fdict = {"path": parts, "length": size}
            self.files.append(fdict)
            if os.path.isdir(full_path):
                self.walk_path(full_path, root)
        return





def get_pieces(paths,piece_size):
    def hash_file(path, piece_length):
        pieces = []
        with open(path,"rb") as fd:
            data = bytearray(piece_length)
            while True:
                length = fd.readinto(data)
                if length == piece_length:
                    pieces.append(sha1(data))
                elif length > 0:
                    pieces.append(sha1(data[:length]))
                else:
                    break
        return bytes().join(pieces)
    piece_layers = []
    for path in paths:
        piece = hash_file(path,piece_size)
        piece_layers.append(piece)
    return bytes().join(piece_layers)

def walk_path(base,files,all_files):
    for item in all_files:
        if os.path.isfile(item):
            desc = {b'length' :os.path.getsize(item),
                    b'path': os.path.relpath(item, base).split(os.sep)}
            files.append(desc)
    return
