from pathlib import Path
import os

torrent_folder = Path("C:\\Users\\asp\\Downloads\\inactiveRecent_Ts").resolve()
search_folder = Path("A:").resolve()
data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)),"data")
