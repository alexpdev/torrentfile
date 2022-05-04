from torrentfile.torrent import TorrentAssembler
from torrentfile.recheck import Checker


content = "V:\\temp"
args = {
    "private": 1,
    "piece_length": 2**14,
    "path": content,
    "announce": ["url1", "url2", "url3", "url4"],
    "httpseeds": ["hurl1"],
    "url_list": ["uurl1", "uurl3"],
    "progress": True,
    "meta_version": 3,
    "comment": "hello world",
    "source": "torrentsource",
}

a = TorrentAssembler(**args)
outfile, meta = a.write()
checker = Checker(outfile, content)
checker.results()
