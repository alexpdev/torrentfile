import os
import math
import hashlib
from pathlib import Path


KIB = 1 << 10
MIB = KIB * KIB
GIB = KIB**3
MIN_BLOCK = 2**14

resolve = lambda x: Path(x).resolve()

def get_piece_length(size):
    """
    Calculate the ideal piece length for bittorrent data.

    Args:
        size (int): total bits of all files incluided in .torrent file

    Returns:
        int: the ideal peace length calculated from the size arguement
    """
    length = size / 1500  # 1500 = ideal number of pieces

    # Check if length is under minimum 16Kb
    if length < 16 * KIB:
        return 16 * KIB

    # Calculate closest perfect power of 2 to target length
    exp = int(math.ceil(math.log2(length)))

    # Check if length is over maximum 8Mb
    if 1 << exp > 8 * MIB:
        return 8 * MIB

    # Ensure total pieces is over 1000
    if size / (1 << exp) < 1000:
        return 1 << (exp-1)
    else:
        return 1 << exp

def path_size(path):
    """Calculate sum of all filesizes within directory.

    Args:
        path (pathlike): The path to start calculating from.

    Returns:
        int: total sum in bytes
    """
    if os.path.isfile(path):
        return os.path.getsize(path)

    #recursive sum for all files in folder
    elif os.path.isdir(path):
        size = 0
        for name in os.listdir(path):
            fullpath = os.path.join(path,name)
            size += path_size(fullpath)
    return size

def get_file_list(path, sort=False):
    """Search directory tree for files.

    Args:
        path (pathlike): path to file or directory base
        sort (bool, optional): return list sorted. Defaults to False.

    Returns:
        [list]: all file paths within directory tree.
    """
    if os.path.isfile(path): return [path]

    # put all files into filelist within directory
    files = list()
    filelist = os.listdir()

    # optional canonical sort of filelist
    if sort: filelist.sort(key=str.lower)

    # recursive for all folders
    for item in filelist:
        full = os.path.join(path,item)
        files.extend(get_file_list(full,sort=sort))
    return files

def folder_stat(path):
    size = path_size(path)
    piece_length = get_piece_length(size)
    return (size, piece_length)

def sha1(data):
    piece = hashlib.sha1()
    piece.update(data)
    return piece.digest()

def sha256(data):
    piece = hashlib.sha256()
    piece.update(data)
    return piece.digest()

def md5(data):
    piece = hashlib.md5()
    piece.update(data)
    return piece.digest()
