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

from tests.context import testdir, testfile
from torrentfile import TorrentFile



def test_torrentfile_dir(testdir):
    path = testdir
    announce = "http://example.com/announce"
    tfile = TorrentFile(path=path, announce=announce, source="nunya", private=1)
    data = tfile.assemble()
    assert data is not None

def test_torrentfile_file(testfile):
    path = testfile
    announce = "http://example.com/announce"
    tfile = TorrentFile(path=path, announce=announce, source="nunya", private=1)
    data = tfile.assemble()
    assert data is not None
