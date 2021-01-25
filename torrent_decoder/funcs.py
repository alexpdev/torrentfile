import re, json, string
from pathlib import Path

"""decoding bincode format"""

def de_str(bits):
	match = re.match(b"(\\d+):",bits)
	word_len, start = int(match.groups()[0]), match.span()[1]
	word = bits[start : start + word_len]
	try:
		word = word.decode("utf-8")
	except:
		word = word.__repr__()
	return word, start + word_len


def de_int(bits):
	obj = re.match(b"i(-?\d+)e", bits)
	return int(obj.group(1)), obj.end()


def de_dict(bits):
	dic, feed = {}, 1
	while not bits[feed:].startswith(b"e"):
		match1, rest = decode(bits[feed:])
		feed += rest
		match2, rest = decode(bits[feed:])
		feed += rest
		dic[match1] = match2
	feed += 1
	return dic, feed

def de_list(bits):
	lst, feed = [], 1
	while not bits[feed:].startswith(b"e"):
		match, rest = decode(bits[feed:])
		lst.append(match)
		feed += rest
	feed += 1
	return lst, feed

def decode(bits):
	if bits.startswith(b"i"):
		match, feed = de_int(bits)
		return match, feed
	elif chr(bits[0]).isdigit():
		match, feed = de_str(bits)
		return match,feed
	elif bits.startswith(b"l"):
		lst, feed = de_list(bits)
		return lst, feed
	elif bits.startswith(b"d"):
		dic, feed = de_dict(bits)
		return dic, feed
	else:
		raise Exception


"""Encode dict to bincode format"""

def encode(self,val):
	if type(val) == str:
		return self.to_str(val)
	elif type(val) == int:
		return self.to_int(val)
	elif type(val) == list:
		return self.to_list(val)
	elif type(val) == dict:
		return self.to_dict(val)
	else:
		return

def to_str(txt):
	size = str(len(txt)).encode("utf-8")
	return size + b":" + txt.encode("utf-8")

def to_int(i):
	return b"i" + b"{i}" + b"e"

def to_list(elems):
	lst = [b"l"]
	for elem in elems:
		encoded = encode(elem)
		lst.append(encoded)
	lst.append(b"e")
	bit_lst = b"".join(lst)
	return bit_lst

def to_dict(dic):
	result = b"d"
	for k,v in dic.items():
		result += b"".join([encode(k), encode(v)])
	return result + b"e"


def decode_torrent(path):
	data = open(path,"rb").read()
	output, feed = decode(data)
	return output






path = Path("C:\\Users\\asp\\Downloads\\inactiveRecent_Ts").resolve()

def make_info_list(path):
	data, output = {}, None
	for p in path.iterdir():
		if ".torrent" in p.name:
			output = decode_torrent(p)
			info = output["info"]
			this = data[p.name] = {}
			if "files" in info:
				data[p.name] = parse_info(info["files"])
			else:
				data[p.name] = info["name"]
	return data

def parse_info(info):
	lst = []
	for dic in info:
		for k in dic:
			if k == "path":
				lst += dic[k]
	return lst




output = make_info_list(path)
json.dump(output,open("formated.json","wt"))


