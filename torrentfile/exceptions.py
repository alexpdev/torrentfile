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
    """
    Error occured during decode process.

    Some value cannot be interpreted by decoder.

    Args:
        val(`any`): Value that cannot be interpreted by decoder.
    """

    def __init__(self, val=None):
        """
        Construct Exception.

        Args:
            val(`any`): Value that cannot be interpreted by decoder.
        """
        message = f"{type(val)} : {val} is of unknown value or type"
        super().__init__(message)


class BenencodingError(Exception):
    """
    Error occured during encoding process.

    A value was discovered that could not be interpreted by encoder.

    Args:
      val(`any`): Value that cannot be interpreted by decoder.
    """

    def __init__(self, val=None):
        """Construct Exception.

        Args:
          val(`any`): Value that cannot be interpreted by decoder.
        """
        message = f"{type(val)} : {val} is of unknown value or type"
        super().__init__(message)


class MissingPathError(Exception):
    """Path parameter is required.

    Creating a .torrent file with no contents seems rather silly.

    Args:
      message(`any`, optional): Value cannot be interpreted by decoder.
    """

    def __init__(self, message=None):
        """
        Construct Exception.

        Args:
          message(`str`, optional): Value cannot be interpreted by decoder.
        """
        self.message = f"Path arguement is missing and required {str(message)}"
        super().__init__(message)
