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

import datetime
import os
import sys

import pyben
import pytest

from tests import dir1, dir2, file1, filemeta1, metafile1, rmpath, tempfile
from torrentfile import execute
from torrentfile.__main__ import main


def test_fix():
    """
    Test dir1 fixture is not None.
    """
    assert dir1 and dir2 and metafile1 and filemeta1 and file1


@pytest.fixture()
def folder(dir1):
    """
    Yield a folder object as fixture.
    """
    sfolder = str(dir1)
    torrent = sfolder + ".torrent"
    yield (sfolder, torrent)
    rmpath(torrent)


def test_cli_v1(folder):
    """
    Basic create torrent cli command.
    """
    folder, torrent = folder
    args = ["torrentfile", "create", folder, "-o", torrent]
    sys.argv = args
    execute()
    assert os.path.exists(torrent)


def test_cli_v2(folder):
    """
    Create torrent v2 cli command.
    """
    folder, torrent = folder
    args = [
        "torrentfile",
        "create",
        folder,
        "--meta-version",
        "2",
        "-o",
        torrent,
    ]
    sys.argv = args
    execute()
    assert os.path.exists(torrent)


def test_cli_v3(folder):
    """
    Create hybrid torrent cli command.
    """
    folder, torrent = folder
    args = [
        "torrentfile",
        "create",
        folder,
        "--meta-version",
        "3",
        "-o",
        torrent,
    ]
    sys.argv = args
    execute()
    assert os.path.exists(torrent)


def test_cli_private(folder):
    """
    Test private cli flag.
    """
    folder, torrent = folder
    args = ["torrentfile", "create", folder, "--private", "-o", torrent]
    sys.argv = args
    main()
    meta = pyben.load(torrent)
    assert "private" in meta["info"]


@pytest.mark.parametrize("piece_length", [2**exp for exp in range(14, 21)])
@pytest.mark.parametrize("version", ["1", "2", "3"])
def test_cli_piece_length(folder, piece_length, version):
    """
    Test piece length cli flag.
    """
    folder, torrent = folder
    args = [
        "torrentfile",
        "-v",
        "create",
        folder,
        "--piece-length",
        str(piece_length),
        "--meta-version",
        version,
        "--progress",
        "0",
        "-o",
        torrent,
    ]
    sys.argv = args
    execute()
    meta = pyben.load(torrent)
    assert meta["info"]["piece length"] == piece_length


@pytest.mark.parametrize("piece_length", [2**exp for exp in range(14, 21)])
@pytest.mark.parametrize("version", ["1", "2", "3"])
def test_cli_announce(folder, piece_length, version):
    """
    Test announce cli flag.
    """
    folder, torrent = folder
    args = [
        "torrentfile",
        "create",
        folder,
        "--piece-length",
        str(piece_length),
        "--meta-version",
        version,
        "--tracker",
        "https://announce.org/tracker",
        "-o",
        torrent,
    ]
    sys.argv = args
    execute()
    meta = pyben.load(torrent)
    assert meta["announce"] == "https://announce.org/tracker"


@pytest.mark.parametrize("version", ["1", "2", "3"])
def test_cli_announce_list(folder, version):
    """
    Test announce-list cli flag.
    """
    folder, torrent = folder
    trackers = [
        "https://announce.org/tracker",
        "https://announce.net/tracker",
        "https://tracker.net/announce",
    ]
    args = [
        "torrentfile",
        "create",
        folder,
        "--meta-version",
        version,
        "-o",
        torrent,
        "--tracker",
    ] + trackers
    sys.argv = args
    execute()
    meta = pyben.load(torrent)
    for url in trackers:
        assert url in [j for i in meta["announce-list"] for j in i]


@pytest.mark.parametrize("piece_length", [2**exp for exp in range(14, 21)])
@pytest.mark.parametrize("version", ["1", "2", "3"])
def test_cli_comment(folder, piece_length, version):
    """
    Test comment cli flag.
    """
    folder, torrent = folder
    args = [
        "torrentfile",
        "create",
        folder,
        "--piece-length",
        str(piece_length),
        "--meta-version",
        version,
        "--magnet",
        "--comment",
        "this is a comment",
        "--progress",
        "1",
        "-o",
        torrent,
    ]
    sys.argv = args
    execute()
    meta = pyben.load(torrent)
    assert meta["info"]["comment"] == "this is a comment"


@pytest.mark.parametrize("piece_length", [2**exp for exp in range(14, 21)])
@pytest.mark.parametrize("version", ["1", "2", "3"])
def test_cli_outfile(dir1, piece_length, version):
    """
    Test outfile cli flag.
    """
    outfile = dir1 + "test.torrent"
    args = [
        "torrentfile",
        "create",
        dir1,
        "--piece-length",
        str(piece_length),
        "--meta-version",
        version,
        "-o",
        outfile,
        "--prog",
        "1",
    ]
    sys.argv = args
    execute()
    assert os.path.exists(outfile)
    rmpath(outfile)


@pytest.mark.parametrize("piece_length", [2**exp for exp in range(14, 21)])
@pytest.mark.parametrize("version", ["1", "2", "3"])
def test_cli_creation_date(folder, piece_length, version):
    """
    Test if torrents created get an accurate timestamp.
    """
    folder, torrent = folder
    args = [
        "torrentfile",
        "create",
        folder,
        "--piece-length",
        str(piece_length),
        "--meta-version",
        version,
        "--comment",
        "this is a comment",
        "-o",
        torrent,
    ]
    sys.argv = args
    execute()
    meta = pyben.load(torrent)
    num = float(meta["creation date"])
    date = datetime.datetime.fromtimestamp(num)
    now = datetime.datetime.now()
    assert date.day == now.day
    assert date.year == now.year
    assert date.month == now.month


@pytest.mark.parametrize("piece_length", [2**exp for exp in range(14, 21)])
@pytest.mark.parametrize("version", ["1", "2", "3"])
def test_cli_created_by(folder, piece_length, version):
    """
    Test if created torrents recieve a created by field in meta info.
    """
    folder, torrent = folder
    args = [
        "torrentfile",
        "-q",
        "create",
        folder,
        "--piece-length",
        str(piece_length),
        "--meta-version",
        version,
        "--comment",
        "this is a comment",
        "-o",
        torrent,
    ]
    sys.argv = args
    execute()
    meta = pyben.load(torrent)
    assert "TorrentFile" in meta["created by"]


@pytest.mark.parametrize("piece_length", [2**exp for exp in range(14, 21)])
@pytest.mark.parametrize("version", ["1", "2", "3"])
def test_cli_web_seeds(folder, piece_length, version):
    """
    Test if created torrents recieve a web seeds field in meta info.
    """
    folder, torrent = folder
    args = [
        "torrentfile",
        "create",
        folder,
        "--piece-length",
        str(piece_length),
        "--meta-version",
        version,
        "-w",
        "https://webseed.url/1",
        "https://webseed.url/2",
        "https://webseed.url/3",
        "-o",
        torrent,
    ]
    sys.argv = args
    execute()
    meta = pyben.load(torrent)
    assert "https://webseed.url/1" in meta["url-list"]


@pytest.mark.parametrize("piece_length", [2**exp for exp in range(14, 21)])
@pytest.mark.parametrize("version", ["1", "2", "3"])
def test_cli_with_debug(folder, piece_length, version):
    """
    Test debug mode cli flag.
    """
    folder, torrent = folder
    args = [
        "torrentfile",
        "-v",
        "create",
        folder,
        "--piece-length",
        str(piece_length),
        "--meta-version",
        version,
        "--comment",
        "this is a comment",
        "-o",
        torrent,
    ]
    sys.argv = args
    execute()
    assert os.path.exists(torrent)


@pytest.mark.parametrize("piece_length", [2**exp for exp in range(14, 21)])
@pytest.mark.parametrize("version", ["1", "2", "3"])
def test_cli_with_source(folder, piece_length, version):
    """
    Test source cli flag.
    """
    folder, torrent = folder
    args = [
        "torrentfile",
        "create",
        folder,
        "--piece-length",
        str(piece_length),
        "--meta-version",
        version,
        "--source",
        "somesource",
        "-o",
        torrent,
    ]
    sys.argv = args
    execute()
    meta = pyben.load(torrent)
    assert meta["info"]["source"] == "somesource"


def test_cli_help():
    """
    Test showing help notice cli flag.
    """
    args = ["-h"]
    sys.argv = args
    try:
        assert execute()
    except SystemExit:
        assert True


@pytest.mark.parametrize("version", ["1", "2", "3"])
@pytest.mark.parametrize("progress", ["0", "1"])
def test_cli_empty_files(dir2, version, progress):
    """
    Test creating torrent with empty files.
    """
    outfile = str(dir2) + ".torrent"
    args = [
        "torrentfile",
        "create",
        str(dir2),
        "--meta-version",
        version,
        "--source",
        "somesource",
        "--prog",
        progress,
        "-o",
        outfile,
    ]
    sys.argv = args

    def walk(root, count):
        """
        Traverse directory to edit files.
        """
        if root.is_file():
            with open(root, "wb") as _:
                return 1
        elif root.is_dir():
            for item in root.iterdir():
                if count >= 2:
                    break
                count += walk(item, count)
        return count

    walk(dir2, 0)
    execute()
    assert os.path.exists(outfile)
    rmpath(outfile)


@pytest.mark.parametrize("ending", ["/", "\\"])
def test_cli_slash_path(dir1, ending):
    """
    Test if output when path ends with a /.
    """
    outfile = str(dir1) + ".torrent"
    if sys.platform != "win32" and ending == "\\":  # pragma: nocover
        ending = "/"
    args = [
        "torrentfile",
        "create",
        "-o",
        outfile,
        "-t",
        "https://announce1.org",
        "--private",
        str(dir1) + ending,
    ]
    sys.argv = args
    execute()
    assert os.path.exists(outfile)
    rmpath(outfile)


@pytest.mark.parametrize("sep", ["/", "\\"])
def test_cli_slash_outpath(dir1, sep):
    """
    Test if output when outpath ends with a /.
    """
    if sys.platform != "win32":
        sep = "/"  # pragma: nocover
    parent = os.path.dirname(dir1) + sep
    args = [
        "torrentfile",
        "create",
        "-t",
        "https://announce1.org",
        "--private",
        "-o",
        parent,
        str(dir1),
    ]
    sys.argv = args
    execute()
    outfile = str(dir1) + ".torrent"
    assert os.path.exists(outfile)
    rmpath(outfile)


@pytest.mark.parametrize(
    "flag", ["-t", "-w", "--announce", "--web-seed", "--http-seed"]
)
def test_cli_announce_path(dir1, flag):
    """
    Test CLI when path is placed after the trackers flag.
    """
    outfile = str(dir1) + ".torrent"
    args = [
        "torrentfile",
        "create",
        "-o",
        outfile,
        flag,
        "https://announce1.org",
        str(dir1),
    ]
    sys.argv = args
    execute()
    assert os.path.exists(outfile)
    rmpath(outfile)


def test_cli_cwd(folder):
    """
    Test outfile cli flag.
    """
    folder, _ = folder
    args = [
        "torrentfile",
        "create",
        "--cwd",
        folder,
    ]
    sys.argv = args
    current = os.getcwd()
    name = os.path.basename(folder)
    outfile = os.path.join(current, name) + ".torrent"
    execute()
    assert os.path.exists(outfile)
    rmpath(outfile)


@pytest.fixture()
def build(dir2):
    """Fixture for testing the build subcommand."""
    dest = os.path.join(os.path.dirname(__file__), "dest")
    if os.path.exists(dest):
        rmpath(dest)
        try:
            os.makedirs(dest)
        except FileExistsError:  # pragma: nocover
            rmpath(dest)
    return os.path.dirname(dir2), dest, dir2


@pytest.mark.parametrize("size", list(range(15, 19)))
@pytest.mark.parametrize("version", [1, 2])
def test_rebuild_subcommand(build, version, size):
    """Test the rebuild CLI subcommand."""
    basedir, dest, content = build
    args = [
        "torrentfile",
        "create",
        str(content),
        "--meta-version",
        str(version),
        "--piece-length",
        str(size),
        "-o",
        str(content) + ".torrent",
    ]
    sys.argv = args
    execute()
    args = ["torrentfile", "rebuild", "-m", basedir, "-c", basedir, "-d", dest]
    sys.argv = args
    counter = execute()
    assert counter > 0


def test_empty_maker(dir1):
    """Test empty create cli."""
    args = ["torrentfile", "create", dir1, "-o", dir1 + ".torrent"]
    sys.argv = args
    execute()
    assert os.path.exists(dir1 + ".torrent")
    rmpath(dir1 + ".torrent")


def test_rename():
    """Test the rename command."""
    tfile = str(tempfile())
    args = ["torrentfile", "create", tfile, "-o", tfile + ".torrent"]
    sys.argv = args
    execute()
    assert os.path.exists(tfile + ".torrent")
    parent = os.path.dirname(tfile)
    temp_path = os.path.join(parent, "renamed.torrent")
    os.rename(tfile + ".torrent", temp_path)
    print(os.listdir(parent))
    args = ["torrentfile", "rename", temp_path]
    sys.argv = args
    execute()
    assert os.path.exists(tfile + ".torrent")
    assert not os.path.exists(temp_path)
    rmpath(tfile + ".torrent", tfile)


@pytest.mark.parametrize("version", ["1", "2", "3"])
def test_cli_default_command(folder, version):
    """Test default command by ommitting command."""
    folder, torrent = folder
    args = [
        "torrentfile",
        "-q",
        folder,
        "--meta-version",
        version,
        "-o",
        torrent,
    ]
    sys.argv = args
    execute()
    assert os.path.exists(torrent)


def test_cli_configfile(folder):
    """Test config cli parameter."""
    args = ["torrentfile", "create", "--config", folder]
    sys.argv = args
    try:
        execute()
    except FileNotFoundError:
        assert True
