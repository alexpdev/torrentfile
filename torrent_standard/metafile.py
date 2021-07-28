import os

class TorrentMeta:
    def __init__(self,announce=None,info=None):
        self.announce = announce
        self.info = info

    def setName(self,name):
        if not self.info:
            self.info = dict()
        self.info["name"] = name

    def setLength(self,length):
        if not self.info:
            self.info = dict()
        self.info["length"] = length


    def setFiles(self,files):
        if not self.info:
            self.info = dict()
        self.info["files"] = files
