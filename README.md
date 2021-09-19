# torrentfile

> Helpful utilities for Bittorrent metafiles.

Create Bittorrent metafiles (".torrent") with granular control over all settings.
Supports Bittorrent version 1 & 2 metafile creation.

![torrentfile](https://github.com/alexpdev/torrentfile/assets/torrentfile.png)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/2da47ec1b5904538a40230f049a02be4)](https://www.codacy.com/gh/alexpdev/torrentfile/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=alexpdev/torrentfile&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/2da47ec1b5904538a40230f049a02be4)](https://www.codacy.com/gh/alexpdev/torrentfile/dashboard?utm_source=github.com&utm_medium=referral&utm_content=alexpdev/torrentfile&utm_campaign=Badge_Coverage)
![GitHub repo size](https://img.shields.io/github/repo-size/alexpdev/torrentfile?style=for-the-badge)
![GitHub](https://img.shields.io/github/license/alexpdev/torrentfile?style=for-the-badge)

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
Torrentfile CLI

optional arguments:
  -h, --help            show this help message and exit
  --version             Display program version.
  --created-by X        Leave out unless specifically instructed otherwise.
  --comment X           include comment in binary data
  -o ~/X.torrent, --outfile ~/X.torrent
                        save output to file.
  -p ~/X, --path ~/X    Path to file of directory of torrent contents.
  --piece-length X      Size of individual pieces of the torrent data.
  --private             torrent will be distributed on a private tracker
  --source X            leave out unless specifically instructed otherwise
  -t url, -a url        "-t url1 url2" add torrent tracker(s).
  --v2, --version2      use Bittorrent V2 protocol if missing V1 is assumed
```

## Meta

Distributed under the GNU LGPL v3 license. See `LICENSE` for more information.

[https://github.com/alexpdev](https://github.com/alexpdev/)
