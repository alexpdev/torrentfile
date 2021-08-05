from pathlib import Path
import json
import os
import shutil
from torrentfile.piecelength import get_piece_length
from torrentfile.metafile import TorrentFile


titles = "WinRAR.v6.02.x64"
path = Path(titles)

def traverse(torrent_files,titles):
    for t in torrent_files:
        if t.name in titles:
            data = t.read_bytes()
            decoder = ()
            tree = decoder.decode_all(data)
            print(tree)

def calculate_total(path):
    total = os.path.getsize(path)
    if not os.path.isdir(path):
        return total
    for item in os.listdir(path):
        fd = os.path.join(path,item)
        total += calculate_total(fd)
    return total

def create(path):
    usage = shutil.disk_usage(path)
    size = os.path.getsize(path)
    st_size = os.stat(path).st_size

def decode_contents(d):
    torrent1 = {}
    for k,v in d.items():
        if isinstance(k,bytes):
            k = k.decode('utf-8',errors="ignore")
        if isinstance(v,bytes):
            v = v.decode('utf-8',errors='ignore')
        elif isinstance(v,dict):
            v = decode_contents(v)
        print(type(k),k)
        torrent1[k] = v
    return torrent1

if __name__ == "__main__":
    total = calculate_total(path) * 8
    piece_size = get_piece_length(total)
    torrentfile = TorrentFile(path,piece_size,announce="http://tracker.com/announce",source="AlphaRatio",private=True)
    info2 = torrentfile.assemble()
