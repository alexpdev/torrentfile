from pathlib import Path
import json
import os
import shutil
from torrentfile.creator import Torrent
from torrentfile.piecelength import get_piece_length

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

if __name__ == "__main__":
    total = calculate_total(path) * 8
    piece_size = get_piece_length(total)
    t = Torrent(path,piece_size)
    torrent = t.create("http://tracker.com/announce",hybrid=True)
    json.dump(torrent,open(path.parent / "a.json","wt"))
