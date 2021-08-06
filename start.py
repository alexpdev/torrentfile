from torrentfile import *

path1 = "WinRAR.v6.02.x64"


if __name__ == "__main__":
    size, piece_length = folder_stat(path1)
    feeder = Feeder(path1,piece_length)
    leaves = []
    for leaf in feeder:
        leaves.append(leaf)
