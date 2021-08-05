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

def _path_size(path):
    if path.is_file():
        return path.stat().st_size
    size = 0
    for item in path.iterdir():
        size += _path_size(item)
    return size

def path_size(path):
    """
    Calculate sum of all file sizes in path.

    Args:
        path (str or pathlike): path to file or dir.

    Returns:
        int: size in bits.
    """
    path = resolve(path)
    return _path_size(path)

def _directory_file_list(path):
    if os.path.isfile(path):
        return [path]
    files = list()
    for item in path.iterdir():
        files.extend(_directory_file_list(item))
    return files

def directory_file_list(path):
    path = resolve(path)
    return _directory_file_list(path)

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
