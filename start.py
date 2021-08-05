import os
import sys

from torrentfile import *

path = "data\\WinRAR.v6.02.x64"


if __name__ == '__main__':
    announce = "http://announce.com/announce"
    torrentfile = TorrentFile(path,announce=announce,private=1,source="me")
    torrentfile.assemble()
    torrentfile.write()
