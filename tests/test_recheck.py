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
Testing functions for the progress module.
"""

import os
import sys
from pathlib import Path

from tests import (dir1, dir2, file1, file2, filemeta1, filemeta2, metafile1,
                   metafile2, rmpath, sizedfiles1, sizedfiles2, sizes)
from torrentfile.cli import main_script as main
from torrentfile.recheck import Checker


def test_fixtures():
    """
    Test fixtures exist.
    """
    assert dir1 and dir2 and file1 and file2
    assert filemeta1 and filemeta2 and metafile1
    assert metafile2 and sizedfiles1 and sizes and sizedfiles2


def test_checker_class(dir1, metafile1):
    """
    Test Checker Class against meta files.
    """
    checker = Checker(metafile1, dir1)
    assert checker.results() == 100


def test_checker_class_alt(dir1, sizedfiles1):
    """
    Test Checker Class against meta files.
    """
    checker = Checker(sizedfiles1, dir1)
    assert checker.results() == 100


def test_checker_first_piece(dir2, sizedfiles2):
    """
    Test Checker Class when first piece is slightly alterred.
    """

    def change(path):
        """
        Change some bytes in file.
        """
        if path.is_file():
            new = b"Something other than what was there before."
            with open(path, "rb") as bfile:
                data = bfile.read()
            new_len = len(new)
            content = b"".join([new, data[new_len:]])
            with open(path, "wb") as bdoc:
                bdoc.write(content)
        elif path.is_dir():
            for item in path.iterdir():
                change(item)

    change(Path(dir2))
    checker = Checker(sizedfiles2, dir2)
    assert checker.results() != 100


def test_checker_first_piece_alt(dir2, sizedfiles2):
    """
    Test Checker Class when first piece is slightly alterred.
    """

    def change(path):
        """
        Change some bytes in file.
        """
        if os.path.isfile(path):
            with open(path, "rb") as bfile:
                data = bfile.read()
            new = b"some_other_bytes_to_use"
            new_len = len(new)
            with open(path, "wb") as wfile:
                wfile.write(new + data[new_len:])
        elif os.path.isdir(path):
            for item in os.listdir(path):
                change(os.path.join(path, item))

    change(dir2)
    checker = Checker(sizedfiles2, dir2)
    assert checker.results() != 100


def test_partial_metafiles(dir2, sizedfiles2):
    """
    Test Checker with data that is expected to be incomplete.
    """

    def shortenfile(path):
        """
        Shorten a few files for testing purposes.
        """
        with open(path, "rb") as bfile:
            data = bfile.read()
        with open(path, "wb") as bfile:
            bfile.write(data[: -(2**10)])

    for item in os.listdir(dir2):
        full = os.path.join(dir2, item)
        if os.path.isfile(full):
            shortenfile(full)

    testdir = os.path.dirname(dir2)
    checker = Checker(sizedfiles2, testdir)
    assert checker.results() != 100


def test_checker_callback(dir1, metafile1):
    """
    Test Checker class with directory that points to nothing.
    """
    Checker.register_callback(lambda *x: print(x))
    checker = Checker(metafile1, str(dir1))
    assert checker.results() == 100


def test_checker_cli_args(dir1, metafile1):
    """
    Test exclusive Checker Mode CLI.
    """
    sys.argv = ["torrentfile", "check", str(metafile1), str(dir1)]
    output = main()
    assert output == 100


def test_checker_parent_dir(dir1, metafile1):
    """
    Test providing the parent directory for torrent checking feature.
    """
    checker = Checker(metafile1, os.path.dirname(dir1))
    assert checker.results() == 100


def test_checker_with_file(file1, filemeta1):
    """
    Test checker with single file torrent.
    """
    checker = Checker(filemeta1, file1)
    assert checker.results() == 100


def test_checker_no_meta_file():
    """
    Test Checker when incorrect metafile is provided.
    """
    try:
        Checker("peaches", "$")
    except FileNotFoundError:
        assert True


def test_checker_wrong_root_dir(metafile1):
    """
    Test Checker when incorrect root directory is provided.
    """
    try:
        Checker(metafile1, "fake")
    except FileNotFoundError:
        assert True


def test_checker_missing(sizedfiles2, dir2):
    """
    Test Checker class when files are missing from contents.
    """
    count = 0
    for fd in Path(dir2).iterdir():
        if fd.is_file() and count < 2:
            rmpath(fd)
    checker = Checker(sizedfiles2, dir2)
    assert int(checker.results()) < 100


def test_checker_class_allfiles(sizedfiles2, dir2):
    """
    Test Checker class when all files are missing from contents.
    """

    def traverse(path):
        """
        Traverse internal subdirectories.
        """
        if path.is_file():
            rmpath(path)
        elif path.is_dir():
            for item in path.iterdir():
                traverse(item)

    traverse(dir2)
    checker = Checker(sizedfiles2, dir2)
    assert int(checker.results()) < 100


def test_checker_class_allpaths(sizedfiles2, dir2):
    """
    Test Checker class when all files are missing from contents.
    """
    for item in Path(str(dir2)).iterdir():
        rmpath(item)
    checker = Checker(sizedfiles2, dir2)
    assert int(checker.results()) < 100


def test_checker_class_half_file(filemeta2, file2):
    """
    Test Checker class with half size single file.
    """
    half = int(os.path.getsize(file2) / 2)
    barr = bytearray(half)
    with open(file2, "rb") as content:
        content.readinto(barr)
    with open(file2, "wb") as content:
        content.write(barr)
    checker = Checker(filemeta2, file2)
    assert int(checker.results()) != 10


def test_checker_missing_singles(dir2, sizedfiles2):
    """
    Test Checker class with half size single file.
    """

    def walk(root):
        """
        Remove first file found.
        """
        if root.is_file():
            rmpath(root)
            return True
        if root.is_dir():
            for item in root.iterdir():
                walk(item)
        return False

    walk(Path(dir2))
    checker = Checker(sizedfiles2, dir2)
    assert int(checker.results()) < 100


def test_checker_result_property(dir1, metafile1):
    """
    Test Checker class with half size single file.
    """
    checker = Checker(metafile1, dir1)
    result = checker.results()
    assert checker.results() == result


def test_checker_simplest(dir1, metafile1):
    """
    Test the simplest example.
    """
    checker = Checker(metafile1, dir1)
    assert checker.results() == 100


def test_checker_empty_files(dir2, sizedfiles2):
    """
    Test Checker when directory contains 0 length files.
    """

    def empty_files(root):
        """
        Dump contents of files.
        """
        if os.path.isfile(root):
            with open(root, "wb") as _:
                pass
            assert os.path.getsize(root) == 0
        elif os.path.isdir(root):
            for item in os.listdir(root):
                return empty_files(os.path.join(root, item))
        return root

    empty_files(dir2)
    checker = Checker(sizedfiles2, dir2)
    assert checker.results() != 100


def test_recheck_wrong_dir(metafile1):
    """
    Test recheck function with directory that doesn't contain the contents.
    """
    grandparent = os.path.dirname(os.path.dirname(metafile1))
    try:
        _ = Checker(metafile1, grandparent)
    except FileNotFoundError:
        assert True
