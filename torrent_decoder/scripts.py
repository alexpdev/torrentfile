import os
import sys
import re
from pathlib import Path

sys.path.append(Path(__file__).resolve().parent)
torrent_folder = Path("A:\\torrents\\.torrents").resolve()
search_folder = Path("A:\\torrents").resolve()
data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

from funcs import decode_torrent_file
from classes import Torrent

""" Iter through directory of .torrent files individually"""

def filter_trackers(torrent):
	public = ['leechers-paradise.org', 'openbittorrent.com', 'demonii.com', 'coppersurfer.tk', 'desync.com', 'opentrackr.org']
	trackers = []
	if "announce_list" in torrent.meta.keys():
		trackers = torrent.meta["announce_list"] + [torrent.meta["announce"]]
		print(trackers)


def select_torrent(torrent_folder):
    for files in Path(torrent_folder).iterdir():
        contents = open(files, "rb").read()
        yield contents


def get_obj(contents):
    torrent = Torrent().read(contents)
	filter_trackers(torrent)
    # print(torrent.meta)


def filter_titles(names):
    """ Identifies filenames based on extension """
    for name in names:
        if re.search("\\.\\w+$", name):
            yield name


if __name__ == "__main__":
    for torrent in select_torrent(torrent_folder):
        get_obj(torrent)


# def look(root,fileset,pairs):
# 	for fname in root.iterdir():
# 		if fname.is_dir():
# 			try:
# 				look(fname,fileset,pairs)
# 			except:
# 				continue
# 		else:
# 			if fname.name in fileset:
# 				pairs.update({str(fname):fname.name})
# 	return pairs


# def make_info_list(path,data_folder):
# 	data,filenames = {},[]
# 	temp_1 = open(os.path.join(data_folder,"temp1.json"),"wt")
# 	for p in path.iterdir():
# 		if ".torrent" in p.name:
# 			output = decode_torrent_file(p)
# 			if "files" in (info := output["info"]):
# 				names = data[p.name] = parse_info(info["files"])
# 				filenames += list(filter_titles(names))
# 			else:
# 				data[p.name] = [info["name"]]
# 				filenames.append(info["name"])
# 	data["file_list"] = filenames
# 	return data
