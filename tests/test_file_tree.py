import os
from tests.context import TEST_DIR, PIECE_LENGTH1
from torrentfile.file_tree import FileTree

class TestFileTree:
    path = TEST_DIR
    piece_length = PIECE_LENGTH1

    def test_file_tree(self):
        tree = FileTree(self.path, self.piece_length)
        assert tree.path == self.path
        assert tree.piece_length == self.piece_length

    def test_file_tree_build(self):
        tree = FileTree(self.path, self.piece_length)
        filetree = tree.build()
        assert type(filetree) == dict
