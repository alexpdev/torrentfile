# torrentfile

![torrentfile](https://github.com/alexpdev/torrentfile/blob/master/assets/torrentfile.png?raw=true)

------

## Bittorrent File Creator (.torrent)

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/2da47ec1b5904538a40230f049a02be4)](https://www.codacy.com/gh/alexpdev/torrentfile/dashboard?utm_source=github.com&utm_medium=referral&utm_content=alexpdev/torrentfile&utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/2da47ec1b5904538a40230f049a02be4)](https://www.codacy.com/gh/alexpdev/torrentfile/dashboard?utm_source=github.com&utm_medium=referral&utm_content=alexpdev/torrentfile&utm_campaign=Badge_Coverage)
![GitHub repo size](https://img.shields.io/github/repo-size/alexpdev/torrentfile?style=plastic)
![GitHub](https://img.shields.io/github/license/alexpdev/torrentfile?style=plastic)

_TorrentFile_ can create torrent files, Check content for accuracy and completeness with a
.torrent file, and display detailed information contained in a .torrent file.

## Features

- Create meta files for Bittorrent v1, v2 and hybrid torrent files.
- Display detailed information contained in torrent file.
- Check/ReCheck content and torrent file for download completion details and data integrity.
- Supports all .torrent files.
- GUI project can be found at [https://github.com/alexpdev/TorrentfileQt](https://github.com/alexpdev/TorrentfileQt)

## Documentation

Documentation can be found in the `./docs` directory, or online at [https://alexpdev.github.io/torrentfile](https://alexpdev.github.io/torrentfile).

## Installation

### via PyPi

`pip install torrentfile`

### via Git

```bash:
git clone https://github.com/alexpdev/torrentfile.git
python setup.py install
```

### download

Or download the latest release from the Release page on github.
[https://github.com/alexpdev/torrentfile/releases](https://github.com/alexpdev/torrentfile/releases)

## CLI Help Message

```bash:
usage: TorrentFile [-h] [-v] [-d] [-p] [-s <source>] [-c <comment>]
                   [-o <path>] [--meta-version <int>] [-l <int>]
                   [-a <url> [<url> ...]] [-r <.torrent>]
                   <content>

Create and/or ReCheck Bittorrent V1, V2, and Hybrid meta files.

positional arguments:
  <content>                             path to content file or directory

optional arguments:
  -h, --help                            show this help message and exit
  -v, --version                         show program version and exit
  -d, --debug                           output debug information
  -p, --private                         create file for private tracker
  -s <source>, --source <source>        specify source tracker
  -c <comment>, --comment <comment>     include a comment in file metadata
  -o <path>, --out <path>               output path for created .torrent file
  --meta-version <int>                  torrent file version.
                                        Options = 1, 2 or 3.
                                        (1) = Bittorrent v1 (Default)
                                        (2) = Bittorrent v2
                                        (3) = Bittorrent v1 & v2 hybrid

  -l <int>, --piece-length <int>        Fixed amount of bytes for each chunk of data. (Default: None)
                                        Acceptable input values include integers 14-24, which
                                        will be interpreted as the exponent for 2^n, or any perfect
                                        power of two integer between 16Kib and 16MiB (inclusive).
                                        Examples:: [--piece-length 14] [-l 20] [-l 16777216]

  -a <url> [<url> ...], --announce <url> [<url> ...]
                                        one or more Bittorrent tracker announce url(s)
                                        Examples: [-a url1 url2 url3]  [--anounce url1]

  -r <.torrent>, --check <.torrent>, --recheck <.torrent>
                                        <.torrent> is the path to a .torrent meta file.
                                        Check <content> data integrity with <.torrent> file.
                                        If this is active, all other options are ignored
                                        (except --debug)
```

## License

Distributed under the GNU LGPL v3. See `LICENSE` for more information.

[https://github.com/alexpdev](https://github.com/alexpdev/)
