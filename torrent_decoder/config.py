from pathlib import Path
import os
torrent_folder = Path("A:\\torrents\\.torrents").resolve()
v_folder = Path("V:\.torrents").resolve()
search_folder = Path("A:\\torrents").resolve()
data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)),"data")
