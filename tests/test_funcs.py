#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os
import json
import sys

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,project_dir)

from torrent_standard.funcs import decode

data_folder = os.path.join(project_dir,"test_data")
torrent_files = os.listdir(data_folder)


class TestFunctions:

    def test_decode(self):
        for part in torrent_files:
            assert part.split(".")[-1].lower() == "torrent"
            path = os.path.join(data_folder,part)
            with open(path,"rb") as data:
                bytes_data = data.read()
                decoded = decode(bytes_data)
                assert len(decoded) == 2
                assert isinstance(decoded[0],dict)
