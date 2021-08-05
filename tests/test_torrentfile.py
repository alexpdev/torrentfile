#! /usr/bin/python3
# -*- coding: utf-8 -*-

from tests.context import TEST_DIR
from torrentfile.metafile import TorrentFile


class TestTorrentFile:

    def test_torrentfile_init(self):
        self.path = TEST_DIR
        tfile = TorrentFile(self.path)
        data = tfile.assemble()
        assert data is not None
