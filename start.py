from torrentfile import *

path1 = "C:\\Users\\asp\\Desktop\\New folder\\Binary.Fortress.Software.LogFusion.Pro.v6.5.Incl.Keygen-BTCR"


if __name__ == "__main__":
    announce = "http://localhost/announce"
    created_by = "ME"
    private = 1
    source = "HERE"
    t = TorrentFile(path=path1,announce=announce,private=private,source=source,created_by=created_by)
    t.assemble()
    t.write()
