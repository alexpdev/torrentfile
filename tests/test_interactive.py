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
Testing functions for the command line interface.
"""

import os

import pyben
import pytest

from tests import file1, file2, filemeta2, torrents
from torrentfile.interactive import select_action
from torrentfile.utils import normalize_piece_length

MOCK = "torrentfile.interactive.get_input"


def test_fixtures():
    """
    Test the fixtures used in module.
    """
    assert filemeta2 and file1 and file2


def test_interactive_create(monkeypatch, file1):
    """
    Test creating torrent interactively.
    """
    mapping = [
        "create",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        file1,
        str(file1) + ".torrent",
        "",
    ]
    it = iter(mapping)
    monkeypatch.setattr(MOCK, lambda *_: next(it))
    select_action()
    assert os.path.exists(str(file1) + ".torrent")


@pytest.mark.parametrize("version", ["1", "2", "3"])
@pytest.mark.parametrize("piece_length", ["23", "18", "131072"])
@pytest.mark.parametrize("announce", ["url1", "urla urlb urlc"])
@pytest.mark.parametrize("url_list", ["ftp url2", "ftp1 ftp2 ftp3"])
@pytest.mark.parametrize("comment", ["Some Comment", "No Comment"])
@pytest.mark.parametrize("source", ["Do", "Ra", "Me"])
def test_inter_create_full(
    file1,
    piece_length,
    announce,
    comment,
    source,
    url_list,
    version,
    monkeypatch,
):
    """
    Test creating torrent interactively with many parameters.
    """
    mapping = [
        "create",
        piece_length,
        announce,
        url_list,
        url_list,
        comment,
        source,
        "Y",
        file1,
        str(file1) + ".torrent",
        version,
    ]
    it = iter(mapping)
    monkeypatch.setattr(MOCK, lambda *_: next(it))
    select_action()
    meta = pyben.load(str(file1) + ".torrent")
    assert meta["info"]["source"] == source
    assert meta["info"]["piece length"] == normalize_piece_length(piece_length)
    assert meta["info"]["comment"] == comment
    assert meta["url-list"] == url_list.split()


@pytest.mark.parametrize("announce", ["url1"])
@pytest.mark.parametrize("url_list", ["ftp url2", "ftp1 ftp2 ftp3"])
@pytest.mark.parametrize("comment", ["Some Comment", "No Comment"])
@pytest.mark.parametrize("source", ["Fa", "So", "La"])
def test_inter_edit_full(
    filemeta2, announce, comment, source, url_list, monkeypatch
):
    """
    Test editing torrent file interactively.
    """
    seq = [
        "edit",
        filemeta2,
        "4",
        announce,
        "1",
        comment,
        "2",
        source,
        "5",
        url_list,
        "",
        "6",
        "Y",
        "DONE",
    ]
    it = iter(seq)
    monkeypatch.setattr(MOCK, lambda *_: next(it))
    select_action()
    meta1 = pyben.load(filemeta2)
    assert meta1["info"]["source"] == source
    assert meta1["info"]["comment"] == comment
    assert meta1["url-list"] == url_list.split()
    assert meta1["info"]["private"] == 1


@pytest.mark.parametrize("announce", ["urla urlb urlc", "urld url2"])
@pytest.mark.parametrize("urllist", ["ftp url2", "ftp1 ftp2 ftp3"])
@pytest.mark.parametrize("cmnt", ["Some Comment"])
@pytest.mark.parametrize("srce", ["Do", "Ra"])
def test_inter_edit_cli(filemeta2, announce, cmnt, srce, urllist, monkeypatch):
    """
    Test editing torrent interactively from CLI.
    """
    seq = [
        "edit",
        filemeta2,
        "4",
        announce,
        "1",
        cmnt,
        "2",
        srce,
        "5",
        urllist,
        urllist,
        "6",
        "Y",
        "DONE",
    ]
    it = iter(seq)
    monkeypatch.setattr(MOCK, lambda *_: next(it))
    select_action()
    meta2 = pyben.load(filemeta2)
    assert meta2["info"]["source"] == srce
    assert meta2["info"]["comment"] == cmnt
    assert meta2["url-list"] == urllist.split()
    assert meta2["info"]["private"] == 1


@pytest.mark.parametrize("torrentclass", torrents())
def test_inter_recheck(torrentclass, monkeypatch, file1):
    """
    Test interactive recheck function.
    """
    outpath = str(file1) + ".torrent"
    torrent = torrentclass(path=file1, outfile=outpath)
    filemeta, _ = torrent.write(outfile=outpath)
    seq = ["recheck", filemeta, str(file1)]
    it = iter(seq)
    monkeypatch.setattr(MOCK, lambda *_: next(it))
    result = select_action()
    assert result == 100
