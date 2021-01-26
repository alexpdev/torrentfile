import os,sys
from pathlib import Path
sys.path.append(Path(__file__).resolve().parent)
import json
import funcs, classes
from config import torrent_folder, search_folder, data_folder


def look(root,filename):
	for fname in root.iterdir():
		if fname.is_dir():
			try:
				look(fname,filename)
			except:
				continue
		else:
			if fname.name == filename:
				return fname

def find_dirs(path,root):
	temp = open("temp.txt","wt")
	for torrent,fp in path.items():
		pairs = look(root,fp)
		if pairs:
			temp.write(str(pairs) + "\n")
			print(torrent)
	return

def find_paths(path,root):
	pairs = open("pairings.txt","wt")
	with open(path,"rt") as fp:
		for line in fp.readlines():
			name,filename = line.split("\t")
			match = look(root,filename)
			if match:
				out = name + "\t" + str(match) + "\n"
				pairs.write(out)
	pairs.close()

def make_info_list(path,data_folder):
	data = {}
	temp_1 = open(os.path.join(data_folder,"temp1.txt"),"wt")
	for p in path.iterdir():
		if ".torrent" in p.name:
			output = funcs.decode_torrent_file(p)
			info = output["info"]
			if "files" in info:
				data[p.name] = parse_info(info["files"])
			else:
				data[p.name] = info["name"]
				out = p.name + "\t" + info["name"] + "\n"
				temp_1.write(out)
	temp_1.close()
	return data

def parse_info(info):
	lst = []
	for dic in info:
		for k in dic:
			if k == "path":
				lst += dic[k]
	return lst


make_info_list(torrent_folder,data_folder)
