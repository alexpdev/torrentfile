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
Testing functions for the sub-action commands from command line args.
"""
import os
import shutil
import sys
from argparse import Namespace
from hashlib import sha1  # nosec
from pathlib import Path
from urllib.parse import quote_plus

import pyben
import pytest

from tests import (dir1, dir2, file1, metafile1, metafile2, rmpath, tempfile,
                   torrents)
from torrentfile.cli import execute
from torrentfile.commands import (find_config_file, info, magnet,
                                  parse_config_file, rebuild, recheck)
from torrentfile.hasher import merkle_root
from torrentfile.utils import ArgumentError


def test_fix():
    """
    Test dir1 fixture is not None.
    """
    assert dir1 and metafile1 and file1 and metafile2 and dir2


def test_magnet_uri(metafile1):
    """
    Test create magnet function digest.
    """
    magnet_link = magnet(metafile1)
    meta = pyben.load(metafile1)
    announce = meta["announce"]
    assert quote_plus(announce) in magnet_link


def test_magnet_hex(metafile1):
    """
    Test create magnet function digest.
    """
    magnet_link = magnet(metafile1)
    meta = pyben.load(metafile1)
    info = meta["info"]
    binfo = sha1(pyben.dumps(info)).hexdigest().upper()
    assert binfo in magnet_link


def test_magnet(metafile1):
    """
    Test create magnet function scheme.
    """
    magnet_link = magnet(metafile1)
    assert magnet_link.startswith("magnet")


def test_magnet_no_announce_list(metafile2):
    """
    Test create magnet function scheme.
    """
    meta = pyben.load(metafile2)
    del meta["announce-list"]
    pyben.dump(meta, metafile2)
    magnet_link = magnet(metafile2)
    assert magnet_link.startswith("magnet")


def test_magnet_empty():
    """
    Test create magnet function scheme.
    """
    try:
        magnet("file_that_does_not_exist")
    except FileNotFoundError:
        assert True


@pytest.mark.parametrize(
    "field",
    ["name", "announce", "source", "comment", "private", "announce-list"],
)
def test_info(field, file1):
    """
    Test the info_command action from the Command Line Interface.
    """
    outfile = str(file1) + ".torrent"
    args = [
        "torrentfile",
        "create",
        "-t",
        "url1",
        "url2",
        "url3",
        "--web-seed",
        "url4",
        "url5",
        "--http-seed",
        "url6",
        "url7",
        "--private",
        "-o",
        outfile,
        "--comment",
        "ExampleComment",
        "--source",
        "examplesource",
        str(file1),
    ]
    sys.argv = args
    execute()

    class Space:
        """
        Stand in substitution for argparse.Namespace object.
        """

        metafile = str(file1) + ".torrent"

    output = info(Space)
    assert field in output


def test_magnet_cli(metafile1):
    """
    Test magnet creation through CLI interface.
    """
    sys.argv[1:] = ["m", str(metafile1)]
    uri = execute()
    assert "magnet" in uri


def test_create_unicode_name(file1):
    """
    Test Unicode information in CLI args.
    """
    parent = os.path.dirname(file1)
    filename = os.path.join(parent, "丂七万丈三与丏丑丒专且丕世丗両丢丣两严丩个丫丬中丮丯.torrent")
    args = [
        "torrentfile",
        "-v",
        "create",
        "-a",
        "tracker_url.com/announce_3456",
        "tracker_url.net/announce_3456",
        "--source",
        "sourcetext",
        "--comment",
        "filename is 丂七万丈三与丏丑丒专且丕世丗両丢丣两严丩个丫丬中丮丯.torrent",
        "-o",
        str(filename),
        str(file1),
    ]
    sys.argv = args
    execute()
    assert os.path.exists(filename)


@pytest.mark.parametrize("blocks", [[], [sha1(b"1010").digest()]])  # nosec
def test_merkle_root_no_blocks(blocks):
    """
    Test running merkle root function with 1 and 0 len lists.
    """
    if blocks:
        assert merkle_root(blocks)
    else:
        assert not merkle_root(blocks)


@pytest.mark.parametrize("torrent", torrents())
def test_mixins_progbar(torrent):
    """
    Test progbar mixins with small file.
    """
    tfile = tempfile(exp=14)
    outfile = str(tfile) + ".torrent"
    msg = "1234abcd" * 80
    with open(tfile, "wb") as temp:
        temp.write(msg.encode("utf-8"))
    args = {
        "path": str(tfile),
        "--prog": "1",
    }
    metafile = torrent(**args)
    output, _ = metafile.write(outfile=outfile)
    assert output == outfile
    rmpath(tfile, outfile)


@pytest.mark.parametrize("torrent", torrents())
def test_mixins_progbar_deep_nesting(torrent):
    """
    Test progbar mixins with small file.
    """
    tfile = tempfile(exp=14)
    dirname = os.path.dirname(tfile)
    nested = "some_super_long_name_to_test_path_length_limits"
    nesting = os.path.join(dirname, nested)
    if not os.path.exists(nesting):
        os.mkdir(nesting)
    tmpfile = os.path.join(nesting, os.path.basename(tfile))
    shutil.move(tfile, tmpfile)
    outfile = str(tmpfile) + ".torrent"
    msg = "1234abcd" * 80
    with open(tmpfile, "wb") as temp:
        temp.write(msg.encode("utf-8"))
    args = {
        "path": str(tmpfile),
        "--prog": "1",
    }
    metafile = torrent(**args)
    output, _ = metafile.write(outfile=outfile)
    assert output == outfile
    rmpath(tmpfile, outfile)


@pytest.fixture
def build(dir2, metafile2):
    """Create fixture for testing rebuild command."""
    basedir = os.path.dirname(dir2)
    parent = os.path.dirname(basedir)
    dest = os.path.join(parent, "dest")
    if os.path.exists(dest):
        rmpath(dest)  # pragma: nocover
    os.mkdir(dest)

    class Namespace:
        """Command line args for rebuild command."""

        metafiles = [os.path.dirname(metafile2)]
        contents = [basedir]
        destination = dest

    yield Namespace
    rmpath(dest)


def test_rebuild(build):
    """Test the rebuild function in the commands module."""
    counter = rebuild(build)
    assert counter > 0


def test_recheck_with_dir():
    """Test running the recheck command with a directory as the metafile."""
    path = os.path.dirname(__file__)

    class Namespace:
        """Emulates the namespace class from argparse module."""

        metafile = path
        content = path

    try:
        recheck(Namespace)
    except ArgumentError:
        assert True


@pytest.fixture(params=[("http-seed", False), ("web-seed", True)])
def config(request):
    """Test config file contents."""
    field, private = request.param
    contents = f"""
[config]
announce =
    url3
    url4
{field} =
    url4
    url5
private = {str(private).lower()}
piece-length = 16
comment = some comment
source = tracker
"""
    return contents


@pytest.fixture(params=[True, False])
def namespace(request, tmp_path):
    """Test fixture for pytest."""
    if request.param:
        ns = Namespace(config=True, config_path=None)
    else:
        ns = Namespace(config=True, config_path=tmp_path / "torrentfile.ini")
    return ns


@pytest.fixture
def configfile(namespace, config):
    """Test fixture for configfile parsing."""
    if namespace.config_path:
        path = namespace.config_path
    else:
        base = Path.home() / ".torrentfile"
        None if os.path.exists(base) else os.mkdir(base)
        path = base / "torrentfile.ini"
    path.write_text(config, encoding="utf8")
    yield namespace
    os.remove(path)


def test_find_config_file(configfile):
    """Test find config file function in commands module."""
    assert find_config_file(configfile) is not None


def test_parse_config_file(configfile):
    """Test parse config file function in commands module."""
    kwargs = {"out": "./somepath"}
    config = find_config_file(configfile)
    parse_config_file(config, kwargs)
    assert "announce" in kwargs


@pytest.mark.parametrize("path", [None, Path.home() / "torrentfile.ini"])
def test_find_config_file_missing(path):
    """Test find config file function with missing config file."""
    ns = Namespace(config=True, config_path=path)
    filename = "torrentfile.ini"
    home = Path.home()
    paths = [
        os.path.join(os.getcwd(), filename),
        home / ".torrentfile" / filename,
        home / ".config" / ".torrentfile" / filename,
    ]
    existing = [i for i in paths if os.path.exists(i)]
    list(map(os.remove, existing))
    try:
        find_config_file(ns)
    except FileNotFoundError:
        assert True
