#! /usr/bin/python3
# -*- coding: utf-8 -*-

from tests.context import TEST_DIR
from torrentfile.metafile import TorrentFile


class TestTorrentFile:

    def test_torrentfile_init(self):
        self.path = TEST_DIR
        announce = "http://example.com/announce"
        tfile = TorrentFile(self.path,announce=announce,source="nunya",private=1)
        data = tfile.assemble()
        assert data is not None
