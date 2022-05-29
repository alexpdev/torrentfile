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
Collection of classes that can be used as Mixins with other base classes.

Classes such as TorrentFile, TorrentFilev2, and all Hasher classes can use the
progress bar mixin.  And any class is eligible to use the callback mixin.
"""
import math
import os
import shutil
import sys
import time
from pathlib import Path


class CbMixin:
    """
    Mixin class to set a callback during hashing procedure.
    """

    _cb = None

    @classmethod
    def set_callback(cls, func):
        """
        Assign a callback to the Hashing class.

        Parameters
        ----------
        func : function
            the callback function
        """
        cls._cb = func  # pragma: nocover


class ProgressBar:
    """
    Holds the state and details of the terminal progress bars.

    Parameters
    ----------
    total : int
        the total amount to be accumulated.
    title : str
        the subject of the progress tracker
    length : int
        the width of the progress bar
    unit : str
        the text representation incremented
    """

    def __init__(self, total, title, length, unit, start):
        """
        Construct the progress bar object and store state of it's properties.
        """
        self.total = total
        self.start = start
        self.length = length
        self.fill = chr(9608)
        self.empty = chr(9617)
        self.state = 0
        self.unit = unit
        self.show_total = total
        if not unit:
            self.unit = ""  # pragma: nocover
        elif unit == "bytes":
            if self.total > 10000000:
                self.show_total = math.floor(self.total / 1048576)
                self.unit = "MiB"
            elif self.total > 10000:
                self.show_total = math.floor(self.total / 1024)
                self.unit = "KiB"
        self.suffix = f"/{self.show_total} {self.unit}"
        if len(title) > start:
            title = title[: start - 1]
        padding = (start - len(title)) * " "
        self.prefix = "".join([title, padding])

    def increment(self, value):
        """
        Increase the state of the progress bar value.

        Parameters
        ----------
        value : int
            the amount to increment the state by.
        """
        self.state += value

    def pbar(self):
        """
        Return the size of the filled portion of the progress bar.

        Returns
        -------
        str :
            the progress bar characters
        """
        if self.state >= self.total:
            fill = self.length
        else:
            fill = math.ceil((self.state / self.total) * self.length)
        empty = self.length - fill
        if self.unit == "MiB":
            state = math.floor(self.state / 1048576)
        elif self.unit == "KiB":
            state = math.floor(self.state / 1024)
        else:
            state = self.state
        progbar = ["[", self.fill * fill, self.empty * empty, "] ", str(state)]
        return "".join(progbar)


class ProgMixin:
    """
    Progress bar mixin class.

    Displays progress of hashing individual files, usefull when hashing
    really big files.

    Methods
    -------
    prog_start
    prog_update
    prog_close
    """

    def prog_start(
        self, total: int, path: str, length: int = 50, unit: str = None
    ):
        """
        Generate a new progress bar for the given file path.

        Parameters
        ----------
        total : int
            the total amount of units accumulating towards.
        path : str
            path to file being hashed.
        length : int
            the number of characters of the actual progress bar.
        unit : str
            the text representation of the value being measured.
        """
        title = path
        width = shutil.get_terminal_size().columns
        if len(str(title)) >= width // 2:
            parts = list(Path(title).parts)
            while len("//".join(parts)) > width // 2 and len(parts) > 0:
                del parts[0]
            title = os.path.join(*parts)
        length = min(length, width // 2)
        start = width - int(length * 1.5)
        self.prog = ProgressBar(total, title, length, unit, start)

    def prog_update(self, val: int):
        """
        Update progress bar with given amount of progress.

        Parameters
        ----------
        val : int
            the number of bytes count the progress bar should increase.
        """
        if self.is_active():
            self.prog.increment(val)
            pbar = self.prog.pbar()
            output = f"{self.prog.prefix}{pbar}{self.prog.suffix}\r"
            sys.stdout.write(output)
            sys.stdout.flush()

    def prog_close(self):
        """
        Finalize the last bits of progress bar.

        Increment the terminal by one line leaving the progress bar in place,
        and deleting the progress bar object to clear a space for the next one.
        """
        if self.is_active():
            sys.stdout.flush()
            sys.stdout.write("\n")
            del self.prog

    def is_active(self):
        """
        Test to see if there is an active progress bar for object.

        Returns
        -------
        bool :
            True if there is, otherwise False.
        """
        if hasattr(self, "prog"):
            return True
        return False


def waiting(msg: str, flag: bool, timeout: int = 180):
    """
    Show loading message while thread completes processing.

    Parameters
    ----------
    msg : str
        Message string printed before the progress bar
    flag : list
        Once flag is filled exit loop
    timeout : int
        max amount of time to run the function.
    """
    then = time.time()
    codes, fill = list(range(9617, 9620)), chr(9619)
    size = idx = 0
    total = shutil.get_terminal_size().columns - len(msg) - 20

    def output(text):
        """
        Print parameter message to the console.

        Parameters
        ----------
        text : str
            output message
        """
        sys.stdout.write(text)
        sys.stdout.flush()

    output("\n")
    while not flag:
        time.sleep(0.16)
        filled = (fill * size) + chr(codes[idx]) + (" " * (total - size))
        output(f"{msg}: {filled}\r")
        idx = idx + 1 if idx + 1 < len(codes) else 0
        size = size + 1 if size < total else 0
        if time.time() - then > timeout:
            break
    output("\n")
