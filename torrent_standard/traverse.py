import os
import hashlib
import json

def sha1(data):
    piece = hashlib.sha1()
    piece.update(data)
    return piece.digest()

def sha256(data):
    piece = hashlib.sha256()
    piece.update(data)
    return piece.digest()

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

def walk_path(base,path,files,paths):
    for fd in sorted(os.listdir(path)):
        p = os.path.join(path,fd)
        if os.path.isfile(p):
            desc = {'path': os.path.relpath(p, base).split(os.sep),
                    'size' :os.path.getsize(p)}
            files.append(desc)
            paths.append(p)
        else:
            walk_path(base,p,files,paths)
    return

def folder_info(path,piece_size):
    info = {}
    paths = []
    info['piece length'] = piece_size
    info['name'] = os.path.basename(path)
    info['files'] = []
    if os.path.isfile(path):
        info['length'] = os.path.getsize(path)
        paths.append(path)
    else:
        walk_path(path,path,info['files'],paths)
    info['pieces'] = get_pieces(paths,piece_size)
    return info





if __name__ == "__main__":
    home = os.environ["USERPROFILE"]
    test_path = path = os.path.join(home,"Documents","Documentation","Folder")
    piece_size = 2 ** 18
    info = folder_info(path,piece_size)
    print(info)
