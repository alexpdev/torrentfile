import os
import hashlib

def sha1(content):
    return hashlib.sha1(content).digest()

class Feeder:

    def __init__(self, path, piece_length):
        self.path = path
        self.name = os.path.basename(path)
        self.piece_length = piece_length
        self.filenames = []
        self.index = 0
        self.current = None
        self.size = 0
        self.pieces = []
        self.generator = None
        self._get_filenames()

    def __next__(self):
        try:
            return next(self.generator)
        except StopIteration:
            self.generator = iter(self)
            return next(self.generator)

    def __iter__(self):
        self.generator = self.leaves()
        return self.generator

    def leaves(self):
        part_size = 0
        partial = False
        counter = 0
        total_pieces = int(self.total_size // self.piece_length) + 1
        piece = bytearray(self.piece_length)
        while self.index < len(self.filenames):
            self.current = open(self.filenames[self.index],"rb")
            if partial:
                temp = bytearray(self.piece_length - part_size)
                self.current.readinto(temp)
                piece[part_size:] = temp
                if len(piece) != self.piece_length:
                    raise Exception
                yield sha1(piece)
                counter += 1
                partial = False
            while True:
                size = self.current.readinto(piece)
                if size == 0: break
                elif size < self.piece_length:
                    partial = True
                    part_size = size
                    break
                else:
                    yield sha1(piece)
                    counter += 1
            self.current.close()
            self.index += 1
        if partial:
            yield sha1(piece[:part_size-1])
        if abs(total_pieces - counter) > 1:
            print(total_pieces)
            raise Exception

    def _single_file(self):
        self.length = os.path.getsize(self.path)
        self.total_size = self.length
        self.filenames.append(self.path)

    def _walk(self, path, level):
        dirlist = sorted(os.listdir(path), key=str.lower)
        for filename in dirlist:
            full = os.path.join(path, filename)
            if os.path.isfile(full):
                self.total_size += os.path.getsize(full)
                final = level[:] + [filename]
                filedict = {'length': os.path.getsize(full), 'path': final}
                self.files.append(filedict)
                self.filenames.append(full)
            elif os.path.isdir(full):
                level.append(filename)
                self._walk(full, level)

    def _get_filenames(self):
        if os.path.isfile(self.path):
            self.length = 0
            return self.single_file()
        self.files = []
        self.total_size = 0
        return self._walk(self.path, [])
