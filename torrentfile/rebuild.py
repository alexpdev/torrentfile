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
Clases and functions for the rebuild or reassemble subcommand.

Re-assemble a torrent into the propper directory structure as indicated by a
torrent meta file, and validate the contents of each file allong the
way. Displays a progress bar for each torrent.
"""
import os
import shutil
from os import PathLike
from pathlib import Path

import pyben


class Metadata:
    """
    Class containing the metadata contents of a torrent file.
    """

    def __init__(self, path: str):
        """
        Construct metadata object for torrent info.

        Parameters
        ----------
        path : str
            path to the .torrent file.
        """
        self.path = os.path.abspath(path)
        self.meta = None
        self.name = None
        self.length = 0
        self.files = []
        self.filenames = set()
        self.extract()

    def extract(self):
        """
        Decode and extract information for the .torrent file.
        """
        self.meta = pyben.load(self.path)
        info = self.meta["info"]
        self.name = info["name"]
        if "length" in info:
            self.length += info["length"]
            self.is_file = True
            self.filenames.add(info["name"])
            self.files.append(
                {
                    "path": Path(self.name).parent,
                    "filename": self.name,
                    "full": self.name,
                    "length": self.length,
                }
            )
        if "files" in info:
            for f in info["files"]:
                path = f["path"]
                full = os.path.join(self.name, *path)
                self.files.append(
                    {
                        "path": Path(full).parent,
                        "filename": path[-1],
                        "full": full,
                        "length": f["length"],
                    }
                )
                self.length += f["length"]
                self.filenames.add(path[-1])
        elif "file tree" in info:
            self._parse_tree(info["file tree"], [self.name])

    def _parse_tree(self, tree: dict, partials: list):
        """
        Parse the file tree dictionary of the torrent metafile.

        Parameters
        ----------
        tree : dict
            the dictionary representation of a file tree.
        partials : list
            list of paths leading up to the current key value.
        """
        for key, val in tree.items():
            if "" in val:
                self.filenames.add(key)
                path = Path(os.path.join(*partials))
                full = Path(os.path.join(path, key))
                length = val[""]["length"]
                self.files.append(
                    {
                        "path": path,
                        "full": full,
                        "filename": key,
                        "length": length,
                    }
                )
                self.length += length
            else:
                self._parse_tree(val, partials + [key])


class Assembler:
    """
    Does most of the work in attempting the structure of torrentfiles.

    Requires three paths as arguments.
    - torrent metafile or directory containing multiple meta files
    - directory containing the contents of meta file
    - directory where torrents will be re-assembled
    """

    def __init__(self, metafile: str, contents: str, dest: str):
        """
        Construct the assembler object.

        Takes two paths as parameters,
        - file or directory containing 1 or more torrent meta files
        - path to where the contents are belived to be located.

        Parameters
        ----------
        metafile : str
            path to torrent metafile or directory containing torrent metafiles.
        contents : str
            path to content or directory containing content that belongs to
            torrentfile.
        dest: str
            path to the directory where rebuild will take place.
        """
        self.metafiles = self._get_metafiles(metafile)
        self.contents = contents
        self.dest = dest
        self.fileinfo = {}
        self.counter = 0

    @staticmethod
    def _get_metafiles(metafile: str):
        """
        Collect all .torrent meta files from give directory or file.

        Parameters
        ----------
        metafile : str
            path to a torrent meta file or directory containing torrent meta
            files.
        """
        metafiles = []
        if os.path.exists(metafile):
            if os.path.isdir(metafile):
                path = os.path.abspath(metafile)
                for filename in os.listdir(path):
                    if filename.lower().endswith(".torrent"):
                        metafiles.append(os.path.join(path, filename))
            elif os.path.isfile(metafile) and metafile.lower().endswith(
                ".torrent"
            ):
                metafiles.append(metafile)
        return metafiles

    def rebuild(self):
        """
        Build the torrent file structure from contents of directory.

        Traverse contents dir and compare discovered files
        with files listed in torrent metadata and copy
        the matches to the destination directory respecting folder
        structures along the way.
        """
        if not self.fileinfo:
            self._traverse_contents(Path(self.contents))
        for path in self.metafiles:
            metadata = Metadata(path)
            for val in metadata.files:
                if val["filename"] in self.fileinfo:
                    self._compare_files(val)
        return self.counter

    def _compare_files(self, val: dict):
        """
        Compare all files with given filename.

        Compare and find which files with the same filename matches
        the length of the given files length and copy the file
        to the destination directory including it's relative file
        structure.

        Parameters
        ----------
        val : dict
            Details about a particular file listed in torrent metadata.
        """
        info = self.fileinfo[val["filename"]]
        for entry in info:
            if entry["length"] != val["length"]:
                continue
            full = os.path.join(self.dest, val["full"])
            if os.path.exists(full):  # pragma: nocover
                print(f"File already found at location {val['filename']}")
                break
            path = self.dest
            for part in val["path"].parts:
                path = os.path.join(path, part)
                if not os.path.exists(path):
                    os.mkdir(path)
            shutil.copy(entry["path"], path)
            self.counter += 1
            if self.counter and self.counter % 20 == 0:
                print(
                    f"Success {self.counter}: {entry['path']} -> {path}"
                )  # pragma: nocover
            break

    def _traverse_contents(self, path: PathLike):
        """
        Traverse the contents directory.

        Recursively walk the directory collecting file names and
        sizes for comparing to contents of torrent file.

        Parameters
        ----------
        path : PathLike
            The current path being traversed.
        """
        if path.is_file():
            info = {
                "path": str(path.resolve()),
                "length": os.path.getsize(path),
            }
            if path.name not in self.fileinfo:
                self.fileinfo[path.name] = [info]
            else:
                self.fileinfo[path.name].append(info)
        elif path.is_dir():
            try:
                for item in path.iterdir():
                    self._traverse_contents(item)
            except PermissionError:  # pragma: nocover
                print(f"Warning {str(path)} skipped due to Permission Error.")
