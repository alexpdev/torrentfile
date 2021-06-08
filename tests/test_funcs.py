#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os
import json
import sys

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,project_dir)

from torrent_standard.funcs import decode

def test_decode():
    torrent = open(".\\tests\\test_data\\25 in 1 Electronic Project On Breadboard Flasher, alarm, detector, ultrasonic, timer, amplifier, no soldering & easy to build.torrent","rb").read()
    decoded = decode(torrent)
    assert type(decoded) == tuple
    print(decoded)


test_decode()
