#! /usr/bin/python3
# -*- coding: utf-8 -*-

#####################################################################
# THE SOFTWARE IS PROVIDED AS IS WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#####################################################################

"""Exceptions used throughout package."""


class BendecodingError(Exception):
    """Error occured during decode process."""

    def __init__(self, val=None):
        """
        Construct Exception.

        Args:
            val(`any`): Value that cannot be interpreted by decoder.
        """
        message = f"{type(val)} : {val} is of unknown value or type"
        super().__init__(message)


class BenencodingError(Exception):
    """Error occured during encoding process."""

    def __init__(self, val=None):
        """
        Construct Exception.

        Args:
            val(`any`): Value that cannot be interpreted by decoder.
        """
        message = f"{type(val)} : {val} is of unknown value or type"
        super().__init__(message)


class MissingArgError(Exception):
    """Missing argument required by program."""

    def __init__(self, message=None):
        """
        Construct Exception.

        Args:
          message(`any`, optional): Value cannot be interpreted by decoder.
        """
        if not message:
            message = "Missing Required Function Arguement"
        super().__init__(message)


class MissingTrackerError(MissingArgError):
    """Announce parameter is required."""

    def __init__(self, message=None):
        """
        Construct Exception.

        Args:
          message(`any`, optional): Value cannot be interpreted by decoder.
        """
        if not message:
            self.message = "Tracker arguement is missing and required"
        super().__init__(message)


class MissingPathError(MissingArgError):
    """Path parameter is required."""

    def __init__(self, message=None):
        """
        Construct Exception.

        Args:
          message(`any`, optional): Value cannot be interpreted by decoder.
        """
        if not message:
            self.message = "Path arguement is missing and required"
        super().__init__(message)


class PieceLengthError(Exception):
    """Piece length must be a power of 2."""

    def __init__(self, val, message=None):
        """
        Construct Exception.

        Args:
          val(`int`): Incorrect piece length value.
          message(`any`, optional): Value cannot be interpreted by decoder.
        """
        if not message:
            message = f"{val} is not a power of 2"
        super().__init__(message)
