# torrentfile

![torrentfile](https://github.com/alexpdev/torrentfile/blob/master/assets/torrentfile.png?raw=true)

----------------------------------------------------

## Bittorrent File Creator (.torrent)

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/2da47ec1b5904538a40230f049a02be4)](https://www.codacy.com/gh/alexpdev/torrentfile/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=alexpdev/torrentfile&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/2da47ec1b5904538a40230f049a02be4)](https://www.codacy.com/gh/alexpdev/torrentfile/dashboard?utm_source=github.com&utm_medium=referral&utm_content=alexpdev/torrentfile&utm_campaign=Badge_Coverage)
![GitHub repo size](https://img.shields.io/github/repo-size/alexpdev/torrentfile?style=plastic)
![GitHub](https://img.shields.io/github/license/alexpdev/torrentfile?style=plastic)

`torrentfile` is a command line application for creating .torrent files for use with bittorrent clients.

## Features

* Simple interface
* Create files for Bittorrent v1
* Create files for Bittorrent v2
* Create files with multiple trackers
* Optionally specify size of individual packets of data for transfer
* Flag torrent file as private for private trackers.

## Installation

### via PyPi

```bash
>> pip install torrentfile
```

### via Git

```bash
>> git clone https://github.com/alexpdev/torrentfile.git
```

## Command Line Options

```bash
usage: torrentfile [-h] [--version] [-p <path>] [-a <url>] [--piece-length <number>] [--private] [-o <path>] [--v2] [--created-by <app>] [--comment <comment>] [--source <source>]
                   [--announce-list [<url> ...]]

Create .torrent files for Bittorrent v1 or v2.

arguments:
  -h, --help            show this help message and exit
  --version             show program version and exit
  -p <path>, --path <path>
                        (required) path to torrent content
  -a <url>, --announce <url>
                        announce url for tracker
  --piece-length <number>
                        specify size in bytes of packets of data to transfer
  --private             use if torrent is for private tracker
  -o <path>, --out <path>
                        specify path for .torrent file
  --v2, --meta-version2
                        use if bittorrent v2 file is wanted
  --created-by <app>
  --comment <comment>   include a comment in .torrent file
  --source <source>     ignore unless instructed otherwise
  --announce-list [<url> ...]
                        for any additional trackers
```

## License

Distributed under the GNU LGPL v3 license. See `LICENSE` for more information.

[https://github.com/alexpdev](https://github.com/alexpdev/)
