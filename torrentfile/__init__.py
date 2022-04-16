#! /usr/bin/python3
# -*- coding: utf-8 -*-

##############################################################################
#    Copyright (C) 2021-current alexpdev
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
##############################################################################
"""
Torrentfile can create Bittorrent metafiles for any content.

Both Bittorrent v1 and v2 are fully supported. Also included is a torrent
torrent file checker, which can verify a .torrent file is formated correctly
as well as validate files and folders against metadata.

Modules:
    metafile: Creation/Validation of v1 .torrent files.
    metafile2: Creation/Validation of v2 .torrent files.
    torrentfile: torrentfiles Command Line Interface implementation.
    exceptions: Custom Exceptions used in package.
    utils: Utilities used throughout package.
"""
import logging
import sys

from torrentfile import utils
from torrentfile.cli import execute
from torrentfile.commands import create, edit, info, magnet, recheck
from torrentfile.interactive import select_action
from torrentfile.version import __version__

__author__ = "alexpdev"

__all__ = ["execute", "create", "edit", "info", "magnet", "recheck"]
