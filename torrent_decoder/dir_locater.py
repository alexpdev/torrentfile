import os
import sys
from pathlib import Path
import json
import funcs

sys.path.append(Path(__file__).resolve().parent)
data_dir = None
root = Path("A:").resolve()
path = Path("C:\\Users\\asp\\Downloads\\inactiveRecent_Ts").resolve()


def look(root,names):
	for fname in root.iterdir():
		try:
			if fname.is_dir():
				look(fname,names)
			elif fname.is_file():
				if isinstance(names,list):
					if fname in names:
						return fname
				else:
					if fname.name == names:
						return fname
		except:
			return None
	return None



# data = json.load(open(path,"rt").read())
def find_dirs(path,root):
	temp = open("temp.txt","wt")
	for torrent,fp in path.items():
		pairs = look(root,fp)
		if pairs:
			temp.write(str(pairs) + "\n")
			print(torrent)
	return

output = funcs.make_info_list(path)
final = find_dirs(output,root)



