import re
import os
import math
from pathlib import Path
import hashlib
from torrentfile.bencode import bencode

__version__ = '0.1.0'

KIB = 2**10
MIB = KIB**2
GIB = KIB**3
MIN_BLOCK = 2**14

class InvalidDataType(Exception):
    pass

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

class Hasher:
    def __init__(self, path, piece_length):
        assert os.path.isfile(path), "Incorrect Path"
        self._path = path
        self._piece_length = piece_length
        self._size = os.path.getsize(self._path)
        self._piece_count = math.ceil(self._size / self._piece_length)

    def _get_data_v1(self):
        pieces = []
        with open(self._path,"rb") as f:
            data = bytearray(self._piece_length)
            while True:
                length = f.readinto(data)
                if length == self._piece_length:
                    pieces.append(sha1(data))
                elif length > 0:
                    pieces.append(sha1(data[:length]))
                else:
                    break
        assert len(pieces) == self._piece_count
        self._pieces = b''.join(pieces)
        return bytes(self._pieces)

    def get_data(self):
        return self._get_data_v1()


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

class TorrentInfo:
    def __init__(self,**kw):
        self.meta = {}
        self.info = self.meta["info"] = {}
        if "version" in kw:
            self.info['version'] = kw["version"]
        if "announce" in kw:
            self.meta['announce'] = kw["announce"]
        if "announce-list" in kw:
            self.meta['announce-list'] = kw['announce-list']
        if 'comment' in kw:
            self.info["comment"] = kw['comment']
        if "private" in kw:
            self.info['private'] = kw["private"]
        else:
            self.info["private"] = False
        if 'created by' in kw:
            self.meta['created by'] = kw['created by']
        else:
            self.meta['created by'] = "Unknown"

    @property
    def announce_list(self):
        return self.meta["announce-list"]

    def set_announce(self,uri):
        self.meta["announce"] = uri

    def set_announce_list(self,arr):
        self.meta["announce-list"] = arr

    def set_comment(self,comment):
        self.info["comment"] = comment

    def set_private(self,private=True):
        self.info["private"] = private

    def set_source(self,source):
        self.info["source"] = source

    def set_name(self,name):
        self.info["name"] = name


class TorrentFiles:
    def __init__(self, path, piece_length):
        self.path = os.path.normpath(path)
        self.pathObj = Path(path)
        self.piece_length = piece_length
        self.name = self.pathObj.name
        self.piece_layers = []
        self.pieces = []
        self.info = []
        self.files = []
        self.base_path = path
        if self.pathObj.is_file():
            pass
        elif self.pathObj.is_dir():
            self.walk_dir(self.name,self.files)


    def walk_dir(self, path, files):
        flist = os.listdir(path).sort(key=lambda x: x.lower())
        for fd in flist:
            npath =  os.path.join(path, fd)
            if os.path.isfile(npath):
                files.append(npath)
            elif os.path.isdir(npath):
                self.walk_dir(npath, files)
            else:
                raise Exception
        return files
