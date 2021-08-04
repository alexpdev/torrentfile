import os
from os.path import dirname, abspath
import sys
from pathlib import Path
sys.path.insert(0,dirname(dirname(abspath(__file__))))
from torrentfile import *



TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),"testdir")

class TestHasher:

    def test_hasher_in(self):
        path = TEST_DIR
        hasher = PieceHasher(path)
        assert hasher.path == path

    def test_hasher_keys(self):
        path = TEST_DIR
        hasher = PieceHasher(path)
        assert hasher.Path == Path(path)
        assert hasher.name == Path(path).name
        assert isinstance(hasher.files ,list)
        assert len(hasher.files) > 1
        print(hasher.files)
        print(hasher.size)
        print(hasher.piece_length)
        print(hasher.paths)

t = TestHasher()
t.test_hasher_in()
t.test_hasher_keys()
