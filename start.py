from torrentfile import execute
from torrentfile.torrent import TorrentAssembler
from torrentfile.recheck import Checker


content = "V:\\Zefrian2"
out = "V:\\Zefrian2.torrent"

args = [
    "recheck",
    out,
    content
]


# args = {
#     "private": 1,
#     "piece_length": 2**14,
#     "path": content,
#     "announce": ["url1", "url2", "url3", "url4"],
#     "httpseeds": ["hurl1"],
#     "url_list": ["uurl1", "uurl3"],
#     "progress": True,
#     "meta_version": 3,
#     "comment": "hello world",
#     "source": "torrentsource",
# }

execute(args)

# a = TorrentAssembler(**args)
# outfile, meta = a.write()
# checker = Checker(outfile, content)
# checker.results()
