#! /usr/bin/python3
# -*- coding: utf-8 -*-

import re

class BencodeDecoder:

    def decode(self, bits):
        if bits.startswith(b"i"):
            match, feed = self.de_int(bits)
            return match, feed
        elif chr(bits[0]).isdigit():
            match, feed = self.de_str(bits)
            return match, feed
        elif bits.startswith(b"l"):
            lst, feed = self.de_list(bits)
            return lst, feed
        elif bits.startswith(b"d"):
            dic, feed = self.de_dict(bits)
            return dic, feed
        else:
            raise Exception

    def de_dict(self, bits):
        dic, feed = {}, 1
        while not bits[feed:].startswith(b"e"):
            match1, rest = self.decode(bits[feed:])
            feed += rest
            match2, rest = self.decode(bits[feed:])
            feed += rest
            dic[match1] = match2
        feed += 1
        return dic, feed

    def de_list(self, bits):
        lst, feed = [], 1
        while not bits[feed:].startswith(b"e"):
            match, rest = self.decode(bits[feed:])
            lst.append(match)
            feed += rest
        feed += 1
        return lst, feed

    def de_str(self, bits):
        match = re.match(b"(\\d+):", bits)
        word_len, start = int(match.groups()[0]), match.span()[1]
        word = bits[start: start + word_len]
        try:
            word = word.decode("utf-8")
        except:
            word = word
        return word, start + word_len

    def de_int(self, bits):
        obj = re.match(b"i(-?\\d+)e", bits)
        return int(obj.group(1)), obj.end()


class BencodeEncoder:

    def encode(self, val):
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

    def to_str(self, txt):
        size = str(len(txt)).encode("utf-8")
        return size + b":" + txt.encode("utf-8")

    def to_int(self, i):
        return b"i" + bytes(str(i)) + b"e"

    def to_list(self, elems):
        lst = [b"l"]
        for elem in elems:
            encoded = self.encode(elem)
            lst.append(encoded)
        lst.append(b"e")
        bit_lst = b"".join(lst)
        return bit_lst

    def to_dict(self, dic):
        result = b"d"
        for k, v in dic.items():
            result += b"".join([self.encode(k), self.encode(v)])
        return result + b"e"


def de_str(bits):
	""" Extracts strings from bencoded data
		Returns: string : [first encoded string found]
	"""
	match = re.match(b"(\\d+):",bits)
	word_len, start = int(match.groups()[0]), match.span()[1]
	word = bits[start : start + word_len]
	try:
		word = word.decode("utf-8")
	except:
		word = word.__repr__()
	return word, start + word_len


def de_int(bits):
	""" Decodes Integers for bencoded data"""
	obj = re.match(b"i(-?\d+)e", bits)
	return int(obj.group(1)), obj.end()


def de_dict(bits):
	""" decodes dictionary from bencoded data """
	dic, feed = {}, 1
	while not bits[feed:].startswith(b"e"):
		match1, rest = bendecode(bits[feed:])
		feed += rest
		match2, rest = bendecode(bits[feed:])
		feed += rest
		dic[match1] = match2
	feed += 1
	return dic, feed

def de_list(bits):
	""" decodes list from bencoded data """
	lst, feed = [], 1
	while not bits[feed:].startswith(b"e"):
		match, rest = bendecode(bits[feed:])
		lst.append(match)
		feed += rest
	feed += 1
	return lst, feed

def bendecode(bits):
	""" Receives bencoded data and decodes it using type decoder functions
	"""
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

def bencode(self,val):
	""" Receives a dictionary and encodes it to Bencode format """
	if type(val) == str:
		return self.to_str(val)
	elif type(val) == int:
		return self.to_int(val)
	elif type(val) == list:
		return self.to_list(val)
	elif type(val) == dict:
		return self.to_dict(val)
	else:
		raise Exception

def to_str(txt):
	""" returns a bencoded str """
	size = str(len(txt)).encode("utf-8")
	return size + b":" + txt.encode("utf-8")

def to_int(i):
	""" returns bencoded int """
	return b"i" + b"{i}" + b"e"

def to_list(elems):
	""" returns bencoded list """
	lst = [b"l"]
	for elem in elems:
		encoded = bencode(elem)
		lst.append(encoded)
	lst.append(b"e")
	bit_lst = b"".join(lst)
	return bit_lst

def to_dict(dic):
	""" returns bencoded dictionary """
	result = b"d"
	for k,v in dic.items():
		result += b"".join([bencode(k), bencode(v)])
	return result + b"e"
