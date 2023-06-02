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

All Bittorrent versions are fully supported.  Torrentfile can also edit,
recheck torrents contents, and create magnet URI's for torrent files.
"""
from torrentfile.cli import execute, main
from torrentfile.commands import create, edit, info, magnet, recheck
from torrentfile.utils import toggle_debug_mode
from torrentfile.version import __version__

toggle_debug_mode(False)

VERSION = __version__

__all__ = [
    "execute",
    "create",
    "edit",
    "info",
    "magnet",
    "recheck",
    "main",
    "VERSION",
]
