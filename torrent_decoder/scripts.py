import os
import sys
import re
from pathlib import Path

sys.path.append(Path(__file__).resolve().parent)
torrent_folder = Path("A:\\torrents\\.torrents").resolve()
search_folder = Path("A:\\torrents").resolve()
data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
from config import v_folder
from funcs import decode_torrent_file
from classes import Torrent

""" Iter through directory of .torrent files individually"""

def filter_trackers(torrent,path):
    if "private" not in torrent.meta.keys():
        print(torrent.meta)
        return path
    # else:
    #     public = ['leechers-paradise.org', 'openbittorrent.com', 'demonii.com', 'coppersurfer.tk', 'desync.com', 'opentrackr.org']
    #     if "announce" in torrent.meta and "announce-list" in torrent.meta:
    #         trackers = [torrent.meta["announce"]] + torrent.meta["announce-list"]
    #         for domain in public:
    #             for tracker in trackers:
    #                 if domain in tracker:
    #                     return path






def select_torrent(torrent_folder):
    for files in Path(torrent_folder).iterdir():
        contents = open(files, "rb").read()
        yield files, contents


def get_obj(contents,path):
    torrent = Torrent().read(contents)
    return filter_trackers(torrent,path)
    # print(torrent.meta)


def filter_titles(names):
    """ Identifies filenames based on extension """
    for name in names:
        if re.search("\\.\\w+$", name):
            yield name


if __name__ == "__main__":
    filter_lst = []
    with open("filter_lst.txt","wt") as fp:
        for path, torrent in select_torrent(v_folder):
            if fpath := get_obj(torrent,path):
                filter_lst.append(fpath)
                print(fpath)
                fp.write(str(fpath))
                os.remove(fpath)
    fp.close()



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
