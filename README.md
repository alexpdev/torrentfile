# torrentfile

![torrentfile](https://github.com/alexpdev/torrentfile/blob/master/assets/torrentfile.png?raw=true)

------

## Bittorrent File Creator (.torrent)

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/2da47ec1b5904538a40230f049a02be4)](https://www.codacy.com/gh/alexpdev/torrentfile/dashboard?utm_source=github.com&utm_medium=referral&utm_content=alexpdev/torrentfile&utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/2da47ec1b5904538a40230f049a02be4)](https://www.codacy.com/gh/alexpdev/torrentfile/dashboard?utm_source=github.com&utm_medium=referral&utm_content=alexpdev/torrentfile&utm_campaign=Badge_Coverage)
![GitHub repo size](https://img.shields.io/github/repo-size/alexpdev/torrentfile?style=plastic)
![GitHub](https://img.shields.io/github/license/alexpdev/torrentfile?style=plastic)

_Torrentfile_ is a CLI for creating .torrent files for bittorrent clients.

## Features

- Simple interface
- Create files for Bittorrent v1
- Create files for Bittorrent v2
- Create files with multiple trackers
- Optionally specify size of individual packets of data for transfer
- Flag torrent file as private for private trackers.
- Check torrentfile against file or directory for match.
- Optional GUI can be found at [https://github.com/Torrentfile-GUI](https://github.com/Torrentfile-GUI)

## Documentation

Documentation can be found by opening your webrowser in the `docs` directory
or by visiting [https://alexpdev.github.io/torrentfile](https://alexpdev.github.io/torrentfile).

## Installation

### via PyPi

`> pip install torrentfile`

### via Git

`> git clone https://github.com/alexpdev/torrentfile.git`

### download

Or download the latest release from the Release page on github.
[https://github.com/alexpdev/torrentfile/releases](https://github.com/alexpdev/torrentfile/releases)

## Using

    usage:    torrentfile -v --version
              torrentfile -h --help
              torrentfile path [-o <dest>] [-a <url>] [--private]
              [--piece-length <n>] [--meta-version <n>] [--source <x>]
              [--announce-list <url2> <...>] [--comment <comment>]

    Create Bittorrent meta files for Bittorrent v1 and v2.

    positional arguments:
      <path>                                Path to content source file or directory.

    optional arguments:
      -h, --help                            show this help message and exit
      -v, --version                         Show program version and exit
      -d, --debug                           Turn on debug mode
      -a <url>, --announce <url>            Primary announce url for Bittorrent Tracker.
      -p <val>, --piece-length <val>        Intiger piece length for content used by Bittorrent Protocol.
                                            Acceptable Input values include 14-35 which will be treated as
                                            an exponent for 2^n power. Otherwise the value must be a
                                            perfect power of 2 between 16KB and 16MB.
                                            i.e. [--piece-length 14] is the same as [--piece-length  16384]
                                            Alternatively, leave blank and let the program calulate the
                                            appropriate piece length.
      --private                             Create file for use with private tracker.
      -o <dest>, --out <dest>               Path to the destination for the output .torrent file.
      --meta-version <n>                    Options = 1, 2 or 3.
                                            (1) = Bittorrent v1;. (Default)
                                            (2) = Bittorrent v2.
                                            (3) = Bittorrent v1 & v2 hybrid.
                                            Specify the Bittorrent Protocol and
                                            formatting version for .torrent file.
      --comment <text>                      Include a comment in file metadata.
      --source <text>                       Specify source.
      --announce-list <url> [<url> ...]     Additional tracker announce URLs.

## License

Distributed under the GNU LGPL v3 license. See `LICENSE` for more information.

[https://github.com/alexpdev](https://github.com/alexpdev/)
