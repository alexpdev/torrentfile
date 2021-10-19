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
"""Context Functions used throughout testing suite."""

import pytest

from tests.context import parameters
from torrentfile import Checker, TorrentFile, TorrentFileHybrid, TorrentFileV2


@pytest.fixture(scope="module", params=parameters())
def testdir(request):
    """Return temp directory."""
    return request.param()


def mktorrent(args, v=None):
    """Torrent making factory."""
    if v == 3:
        torrent = TorrentFileHybrid(**args)
    elif v == 2:
        torrent = TorrentFileV2(**args)
    else:
        torrent = TorrentFile(**args)
    torrent.assemble()
    return torrent.write()


@pytest.mark.parametrize("version", [1, 2, 3])
def test_metafile_checker(testdir, version):
    """Test metadata."""
    args = {"announce": "announce", "path": testdir, "private": 1}
    outfile, _ = mktorrent(args, v=version)
    checker = Checker(outfile, testdir)
    status = checker.check()
    assert status == "100%"  # nosec
