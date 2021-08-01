import re
import os
import math
from pathlib import Path
import hashlib

__version__ = '0.1.0'

KIB = 2**10
MIB = KIB**2
GIB = KIB**3
MIN_BLOCK = 2**14

class InvalidDataType(Exception):
    pass

def to_str(txt):
	""" returns a bencoded str """
	size = str(len(txt)).encode("utf-8")
	return size + b":" + txt.encode("utf-8")

def to_int(i):
	""" returns bencoded int """
	return b"i" + b"{i}" + b"e"

def to_list(elems):
	""" returns bencoded list """
	lst = [b"l"]
	for elem in elems:
		encoded = bencode(elem)
		lst.append(encoded)
	lst.append(b"e")
	bit_lst = b"".join(lst)
	return bit_lst

def to_dict(dic):
	""" returns bencoded dictionary """
	result = b"d"
	for k,v in dic.items():
		result += b"".join([bencode(k), bencode(v)])
	return result + b"e"

def de_dict(s):
    dic, feed = {}, 1
    while not s[feed:].startswith(b"e"):
        match1, rest = bendecode(s[feed:])
        feed += rest
        match2, rest = bendecode(s[feed:])
        feed += rest
        dic[match1] = match2
    feed += 1
    return dic, feed

def de_list(s):
    lst, feed = [], 1
    while not s[feed:].startswith(b"e"):
        match, rest = bendecode(s[feed:])
        lst.append(match)
        feed += rest
    feed += 1
    return lst, feed

def de_str(s):
    match = re.match(b"(\\d+):", s)
    word_len, start = int(match.groups()[0]), match.span()[1]
    word = s[start: start + word_len]
    try:
        word = word.bendecode("utf-8")
    except:
        word = word
    return word, start + word_len

def de_int(s):
    obj = re.match(b"i(-?\\d+)e", s)
    return int(obj.group(1)), obj.end()

def bencode(self,val):
	""" Receives a dictionary and encodes it to Bencode format """
	if type(val) == str:
		return self.to_str(val)
	elif type(val) == int:
		return self.to_int(val)
	elif type(val) == list:
		return self.to_list(val)
	elif type(val) == dict:
		return self.to_dict(val)
	else:
		raise InvalidDataType

def bendecode(s):
    if s.startswith(b"i"):
        match, feed = de_int(s)
        return match, feed
    elif chr(s[0]).isdigit():
        match, feed = de_str(s)
        return match, feed
    elif s.startswith(b"l"):
        lst, feed = de_list(s)
        return lst, feed
    elif s.startswith(b"d"):
        dic, feed = de_dict(s)
        return dic, feed
    else:
        raise InvalidDataType

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
