# torrentfile

> Helpful utilities for Bittorrent metafiles.

Create Bittorrent metafiles (".torrent") with granular control over all settings.
Supports Bittorrent version 1 & 2 metafile creation.

![torrentfile](assets/torrentfile.png)

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
