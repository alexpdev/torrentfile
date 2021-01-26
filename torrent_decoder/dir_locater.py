import os
import sys
from pathlib import Path
import json
import funcs

sys.path.append(Path(__file__).resolve().parent)
data_dir = None
path = Path("C:\\Users\\asp\\Downloads\\inactiveRecent_Ts").resolve()


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



# data = json.load(open(path,"rt").read())
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

root = Path("A:").resolve()
path = Path("C:\\Users\\asp\\Documents\\Code\\Github-Repos\\torrent_standard\\temp1.txt").resolve()
find_paths(path,root)

# output = funcs.make_info_list(path)
# final = find_dirs(output,root)



