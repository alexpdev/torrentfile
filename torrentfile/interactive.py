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
Module contains the procedures used for Interactive Mode.
"""

import os
import shutil
import sys

import pyben

from torrentfile.edit import edit_torrent
from torrentfile.recheck import Checker
from torrentfile.torrent import TorrentFile, TorrentFileHybrid, TorrentFileV2


def get_input(*args: tuple):  # pragma: no cover
    """
    Determine appropriate input function to call.

    Parameters
    ----------
    *args : tuple
        Arbitrary number of args to pass to next function

    Returns
    -------
    str
        The results of the function call.
    """
    if len(args) == 2:
        return _get_input_loop(*args)
    return _get_input(*args)


def _get_input(txt: str):  # pragma: no cover
    """
    Gather information needed from user.

    Parameters
    ----------
    txt : str
        The message usually containing instructions for the user.

    Returns
    -------
    str
        The text input received from the user.
    """
    value = input(txt)
    return value


def _get_input_loop(txt, func):  # pragma: no cover
    """
    Gather information needed from user.

    Parameters
    ----------
    txt : str
        The message usually containing instructions for the user.
    func : function
        Validate/Check user input data, failure = retry, success = continue.

    Returns
    -------
    str
        The text input received from the user.
    """
    while True:
        value = input(txt)
        if func and func(value):
            return value
        if not func or value == "":
            return value
        showtext(f"Invalid input {value}: try again")


def showtext(txt):
    """
    Print contents of txt to screen.

    Parameters
    ----------
    txt : str
        text to print to terminal.
    """
    sys.stdout.write(txt)


def showcenter(txt: str):
    """
    Print text to screen in the center position of the terminal.

    Parameters
    ----------
    txt : str
        the preformated message to send to stdout.
    """
    termlen = shutil.get_terminal_size().columns
    padding = " " * int(((termlen - len(txt)) / 2))
    string = "".join(["\n", padding, txt, "\n"])
    showtext(string)


def select_action():
    """
    Operate TorrentFile program interactively through terminal.
    """
    showcenter("TorrentFile: Starting Interactive Mode")
    action = get_input(
        "Enter the action you wish to perform.\n"
        "Action ( Create (c) | Edit (e) | Recheck (r) ): "
    )
    action = action.lower()

    if "create" in action or action == "c":
        return create_torrent()

    if "check" in action or action == "r":
        return recheck_torrent()

    if "edit" in action or action == "e":
        return edit_action()
    print("Unable to recognize input.  Please try again.")  # pragma: nocover
    return select_action()  # pragma: nocover


def recheck_torrent():
    """
    Check torrent download completed percentage.
    """
    showcenter("Check Torrent")
    msg = "Enter path to torrent contents, and corresponding torrent metafile."
    showtext(msg)
    metafile = get_input(
        "Conent Path (downloads/complete/torrentname):", os.path.exists
    )
    contents = get_input("Metafile (*.torrent): ", os.path.exists)
    checker = Checker(metafile, contents)
    results = checker.results()
    showtext(f"Completion for {metafile} is {results}%")
    return results


def create_torrent():
    """
    Create new torrent file interactively.
    """
    showcenter("Create Torrent")
    showtext(
        "\nEnter values for each of the options for the torrent creator, "
        "or leave blank for program defaults.\nSpaces are considered item "
        "seperators for options that accept a list of values.\nValues "
        "enclosed in () indicate the default value, while {} holds all "
        "valid choices available for the option.\n\n"
    )
    creator = InteractiveCreator()
    return creator


def edit_action():
    """
    Edit the editable values of the torrent meta file.
    """
    showcenter("Edit Torrent")
    metafile = get_input("Metafile(.torrent): ", os.path.exists)
    dialog = InteractiveEditor(metafile)
    dialog.show_current()
    dialog.edit_props()


class InteractiveEditor:
    """
    Interactive dialog class for torrent editing.
    """

    def __init__(self, metafile: str):
        """
        Initialize the Interactive torrent editor guide.

        Parameters
        ----------
        metafile : str
            user input string identifying the path to a torrent meta file.
        """
        self.metafile = metafile
        self.meta = pyben.load(metafile)
        self.info = self.meta["info"]

        self.args = {
            "url-list": self.meta.get("url-list", None),
            "httpseeds": self.meta.get("httpseeds", None),
            "announce": self.meta.get("announce-list", None),
            "source": self.info.get("source", None),
            "private": self.info.get("private", None),
            "comment": self.info.get("comment", None),
        }

    def show_current(self):
        """
        Display the current met file information to screen.
        """
        out = "Current properties and values:\n"
        longest = max([len(label) for label in self.args]) + 3
        for key, val in self.args.items():
            txt = (key.title() + ":").ljust(longest) + str(val)
            out += f"\t{txt}\n"
        showtext(out)

    def sanatize_response(self, key, response):
        """
        Convert the input data into a form recognizable by the program.

        Parameters
        ----------
        key : str
            name of the property and attribute being eddited.
        response : str
            User input value the property is being edited to.
        """
        if key in ["announce", "url-list", "httpseeds"]:
            val = response.split()
        else:
            val = response
        self.args[key] = val

    def edit_props(self):
        """
        Loop continuosly for edits until user signals DONE.
        """
        while True:
            showcenter(
                "Choose the number for a propert the needs editing."
                "Enter DONE when all editing has been completed."
            )

            props = {
                1: "comment",
                2: "source",
                3: "private",
                4: "tracker",
                5: "web-seed",
                6: "httpseeds",
            }

            args = {
                1: "comment",
                2: "source",
                3: "private",
                4: "announce",
                5: "url-list",
                6: "httpseeds",
            }

            txt = ", ".join((str(k) + ": " + v) for k, v in props.items())
            prop = get_input(txt)
            if prop.lower() == "done":
                break

            if prop.isdigit() and 0 < int(prop) < 6:
                key = props[int(prop)]
                key2 = args[int(prop)]
                val = self.args.get(key2)
                showtext(
                    "Enter new property value or leave empty for no value."
                )
                response = get_input(f"{key.title()} ({val}): ")
                self.sanatize_response(key2, response)

            else:
                showtext("Invalid input: Try again.")
        edit_torrent(self.metafile, self.args)


class InteractiveCreator:
    """
    Class namespace for interactive program options.
    """

    def __init__(self):
        """
        Initialize interactive meta file creator dialog.
        """
        self.kwargs = {
            "announce": None,
            "url_list": None,
            "private": None,
            "source": None,
            "comment": None,
            "piece_length": None,
            "outfile": None,
            "path": None,
            "httpseeds": None,
        }
        self.outfile, self.meta = self.get_props()

    def get_props(self):
        """
        Gather details for torrentfile from user.
        """
        piece_length = get_input(
            "Piece Length (empty=auto): ", lambda x: x.isdigit()
        )

        self.kwargs["piece_length"] = piece_length
        announce = get_input(
            "Tracker list (empty): ", lambda x: isinstance(x, str)
        )

        if announce:
            self.kwargs["announce"] = announce.split()

        url_list = get_input(
            "Web Seed {GetRight} list (empty): ", lambda x: isinstance(x, str)
        )

        httpseeds = get_input(
            "Web Seed {Hoffman} list (empty): ", lambda x: isinstance(x, str)
        )

        if url_list:
            self.kwargs["url_list"] = url_list.split()
        if httpseeds:
            self.kwargs["httpseeds"] = httpseeds.split()
        comment = get_input("Comment (empty): ", None)

        if comment:
            self.kwargs["comment"] = comment
        source = get_input("Source (empty): ", None)

        if source:
            self.kwargs["source"] = source

        private = get_input(
            "Private Torrent? {Y/N}: (N)", lambda x: x in "yYnN"
        )

        if private and private.lower() == "y":
            self.kwargs["private"] = 1

        contents = get_input("Content Path: ", os.path.exists)
        self.kwargs["path"] = contents

        outfile = get_input(
            f"Output Path ({contents}.torrent): ",
            lambda x: os.path.exists(os.path.dirname(x)),
        )

        if outfile:
            self.kwargs["outfile"] = outfile

        meta_version = get_input(
            "Meta Version {1,2,3}: (1)", lambda x: x in "123"
        )

        showcenter(f"creating {outfile}")

        if meta_version == "3":
            torrent = TorrentFileHybrid(**self.kwargs)
        elif meta_version == "2":
            torrent = TorrentFileV2(**self.kwargs)
        else:
            torrent = TorrentFile(**self.kwargs)
        return torrent.write()
