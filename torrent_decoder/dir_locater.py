import os
import sys
import re
from pathlib import Path

sys.path.append(Path(__file__).resolve().parent)
import json
import classes
import funcs
from config import data_folder, search_folder, torrent_folder

def look(root,fileset,pairs):
	for fname in root.iterdir():
		if fname.is_dir():
			try:
				look(fname,fileset,pairs)
			except:
				continue
		else:
			if fname.name in fileset:
				pairs.update({str(fname):fname.name})
	return pairs


def find_dirs(file_list,root):
	fileset = set(file_list)
	matches = {}
	pairs = look(root,fileset,matches)
	json.dump(pairs,open(os.path.join(data_folder,"pairs.json"),"wt"))
	return


def make_info_list(path,data_folder):
	data,filenames = {},[]
	temp_1 = open(os.path.join(data_folder,"temp1.json"),"wt")
	for p in path.iterdir():
		if ".torrent" in p.name:
			output = funcs.decode_torrent_file(p)
			if "files" in (info := output["info"]):
				names = data[p.name] = parse_info(info["files"])
				filenames += list(filter_titles(names))
			else:
				data[p.name] = [info["name"]]
				filenames.append(info["name"])
	data["file_list"] = filenames
	json.dump(data,temp_1)
	return data

def parse_info(info):
	lst = []
	for dic in info:
		for k in dic:
			if k == "path":
				lst += dic[k]
	return lst

def filter_titles(names):
	for name in names:
		if re.search("\\.\\w+$",name):
			yield name

data = make_info_list(torrent_folder,data_folder)
find_dirs(data["file_list"],search_folder)

