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
    padding : int
        the size of the gap between title and progress bar
    """

    def __init__(self, total, title, length, unit, start):
        """
        Construct the progress bar object and store state of it's properties.
        """
        self.active = True
        self.total = total
        self.title = title
        self.length = length
        self.unit = unit
        self.fill = chr(9608)
        self.empty = chr(9617)
        self.state = 0
        self.start = start

    def increment(self, value):
        """
        Increase the state of the progress bar value.

        Parameters
        ----------
        value : int
            the amount to increment the state by.
        """
        self.state += value

    def progbar(self):
        """
        Return the size of the filled portion of the progress bar.

        Returns
        -------
        str :
            the progress bar characters
        """
        if self.state == self.total:
            fill = self.length
        else:
            fill = int((self.state / self.total) * self.length)
        empty = self.length - fill
        pbar = (self.fill * fill) + (self.empty * empty)
        return pbar

    def center(self):
        """
        Return the prefix plus the title plus the padding.

        Returns
        -------
        str :
            the prefix to the progress bar characters
        """
        if len(self.title) > self.length:
            title = self.title[: self.length]
        else:
            title = self.title
        padding = (self.start - len(title)) * " "
        return "".join([title, padding])

    def stats(self):
        """
        Return the suffix after progress bar.

        Returns
        -------
        str :
            the suffix to the progress bar characters
        """
        total = self.total
        state = self.state
        unit = self.unit if self.unit else ""
        if self.unit == "bytes":
            if self.total > 100000:
                total = math.floor(self.total / 1048576)
                state = math.floor(self.state / 1048576)
                unit = "MiB"
            elif self.total > 10000:  # pragma: nocover
                total = math.floor(self.total / 1024)
                state = math.floor(self.state / 1024)
                unit = "KiB"
        return f" {state}/{total} {unit}"


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

    def prog_start(self, total, path, length=50, unit=None):
        """
        Generate a new progress bar for the given file path.

        Parameters
        ----------
        total : int
            the total amount of units accumulating towards.
        path : str
            path to file being hashed.
        indent : int
            the level of padding needed before the title
        length : int
            the number of characters of the actual progress bar.
        unit : str
            the text representation of the value being measured.
        """
        title = os.path.basename(path)
        width = shutil.get_terminal_size().columns
        extra = "[]/  "
        begin = length + len(extra) + (length // 2)
        start = width - begin
        self.prog = ProgressBar(total, title, length, unit, start)

    def prog_update(self, val):
        """
        Update progress bar with given amount of progress.

        Parameters
        ----------
        val : int
            the number of bytes count the progress bar should increase.
        end : bool
            if this is the last print of the progress bar
        """
        if self.is_active():
            self.prog.increment(val)
            if self.prog.total >= self.prog.state:
                pbar = self.prog.progbar()
                title = self.prog.center()
                stats = self.prog.stats()
                output = f"\r{title} [{pbar}] {stats}"
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
