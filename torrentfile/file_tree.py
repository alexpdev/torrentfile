import os
from torrentfile.feeder import Feeder
from torrentfile.utils import sha256

class InvalidDirectoryItem(Exception):
    pass

BLOCK_SIZE = 2**16

class PiecesRoot:
    def __init__(self,path,size):
        self.path = path
        self.size = size
        self.leaves = []
        self.tree = {}

    def get_root(self):
        level = []
        leaves = self.leaves
        while len(level) > 1:
            a = 0
            b = 1
            while a < len(self.leaves):
                if a == len(self.leaves) - 1:
                    item1 = leaves[a]
                    item2 = bytearray(0)
                else:
                    item1 = leaves[a]
                    item2 = leaves[b]
                comb = item1 + item2
                level.append({sha256(comb), [item1,item2]})
                a += 2
                b += 2
            leaves = level
            level = []
        self.tree = level[0]

    def split_file(self):
        feeder = Feeder([self.path],self.size,sha256=True)
        for leaf in feeder:
            self.leaves.append(leaf)
        self.get_root()


def pieces_root(*args):
    pass

class FileTree:

    def __init__(self, path, piece_length):
        self.path = path
        self.piece_length = piece_length
        self.tree = {}

    def _build_tree(self, path, tree):
        name = os.path.basename(path)
        if os.path.isfile(path):
            size = os.path.getsize(path)
            tree[name] = {"" : {
                "length": size,
                "pieces root": pieces_root(path, self.piece_length, size)
            }}
        elif os.path.isdir(path):
            filelist = os.listdir(path)
            filelist.sort(key=str.lower)
            tree[name] = {}
            for item in filelist:
                full = os.path.join(path,item)
                self._build_tree(full, tree[name])
        else:
            raise InvalidDirectoryItem

    def build(self):
        self._build_tree(self.path, self.tree)
        return self.tree
