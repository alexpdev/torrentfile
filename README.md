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

- Simple interface
- Create torrent files.
- Display detailed information contained in torrent file.
- Check torrent content for accuracy and completeness with a .torrent file.
- Support for Bittorrent Version 1, 2, and hybrid .torrent files.
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

## Using

```bash:
usage: torrentfile [-h] [-v] [-d] [-p] [-s <source>] [-c <comment>]
                   [-a <url> [<url> ...]] [-o <path>] [--meta-version <int>]
                   [-l <int>] [-r <.torrent>]
                   <content>

Create or Re-Check Bittorrent meta files for Bittorrent v1, v2 or v1, v2 combo
Hybrids.

positional arguments:
  <content>                                  path to .torrent file content

optional arguments:
  -h, --help                                 show this help message and exit
  -v, --version                              show program version and exit
  -d, --debug                                output debug information
  -p, --private                              create .torrent file for private tracker
  -s <source>, --source <source>             specify source
  -c <comment>, --comment <comment>          include a comment in file metadata
  -o <path>, --out <path>                    output path for created .torrent file

  -a <url> [<url> ...], --announce <url> [<url> ...]
                                             One or more announce urls for Bittorrent tracker

  --meta-version <int>                       .torrent file version.
                                             Options = 1, 2 or 3.
                                             (1) = Bittorrent v1;. (Default)
                                             (2) = Bittorrent v2.
                                             (3) = Bittorrent v1 & v2 hybrid.

  -l <int>, --piece-length <int>             piece length used by Bittorrent transfer protocol.
                                             Acceptable values include 14-24, will be treated as the
                                             exponent for 2^n power, or any power of 2 integer in 16KB-16MB.
                                             e.g. `--piece-length 14` is the same as `--piece-length  16384`

  -r <.torrent>, --re-check <.torrent>       <.torrent> is the path to a .torrent meta file.
                                             Check <content> data integrity with <.torrent> file.
                                             When this option is active, all other options are ignored (except -d).
```

## License

Distributed under the GNU LGPL v3. See `LICENSE` for more information.

[https://github.com/alexpdev](https://github.com/alexpdev/)
