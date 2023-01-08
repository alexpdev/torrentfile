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

from torrentfile.utils import debug_is_on


class CbMixin:
    """
    Mixin class to set a callback during hashing procedure.
    """

    @classmethod
    def cb(cls, *args, **kwargs):
        """Do nothing."""

    @classmethod
    def set_callback(cls, func):
        """
        Assign a callback to the Hashing class.

        Parameters
        ----------
        func : Callable
            the callback function
        """
        cls.cb = func  # pragma: nocover


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
    start : int
        column where the progress bar should be drawn
    """

    def __init__(
        self, total: int, title: str, length: int, unit: str, start: int
    ):
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
            if self.total > 1_000_000_000:
                self.show_total = math.floor(self.total / (2**30))
                self.unit = "GiB"
            elif self.total > 1_000_000:
                self.show_total = math.floor(self.total / 1048576)
                self.unit = "MiB"
            elif self.total > 10000:
                self.show_total = math.floor(self.total / 1024)
                self.unit = "KiB"
        self.suffix = f"/{self.show_total} {self.unit}"
        title = str(title)
        if len(title) > start:
            title = title[: start - 1]  # pragma: nocover
        padding = (start - len(title)) * " "
        self.prefix = "".join([title, padding])

    def get_progress(self) -> str:
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
        empt = self.length - fill
        if self.unit == "GiB":
            state = math.floor(self.state / (2**30))
        elif self.unit == "MiB":
            state = math.floor(self.state / 1048576)
        elif self.unit == "KiB":
            state = math.floor(self.state / 1024)
        else:
            state = self.state
        progbar = ["|", self.fill * fill, self.empty * empt, "| ", str(state)]
        return "".join(progbar)


class ProgMixin:
    """
    Progress bar mixin class.

    Displays progress of hashing individual files, usefull when hashing
    really big files.
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
            while (len("//".join(parts)) > (width // 2)) and (len(parts) > 0):
                del parts[0]
            if parts:
                title = os.path.join(*parts)
            else:
                title = os.path.basename(path)  # pragma: nocover
        length = min(length, width // 2)
        start = width - int(length * 1.5)
        self.prog = ProgressBar(total, title, length, unit, start)

    def prog_update(self, val: int):
        """
        Update progress bar.

        Using the value provided, increment the progress bar by that value.

        Parameters
        ----------
        val : int
            the number of bytes count the progress bar should increase.
        """
        if self.is_active():
            self.prog.state += val
            pbar = self.prog.get_progress()
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

    def is_active(self) -> bool:
        """
        Test to see if there is an active progress bar for object.

        Returns
        -------
        bool :
            True if there is, otherwise False.
        """
        if not debug_is_on() and hasattr(self, "prog"):
            return True
        return False


def waiting(msg: str, flag: list, timeout: int = 20):
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

    def output(text: str):
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
    time.sleep(0.16)
    while len(flag) == 0:
        time.sleep(0.16)
        filled = (fill * size) + chr(codes[idx]) + (" " * (total - size))
        output(f"{msg}: {filled}\r")
        idx = idx + 1 if idx + 1 < len(codes) else 0
        size = size + 1 if size < total else 0
        if time.time() - then > timeout:
            break
    output("\n")
