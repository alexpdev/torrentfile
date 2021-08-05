import os
import sys
import pytest
from pathlib import Path
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from torrentfile import *
from tests.context import TEST_DIR

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
