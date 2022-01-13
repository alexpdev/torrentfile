# TorrentFile

![torrentfile](https://github.com/alexpdev/torrentfile/blob/master/assets/torrentfile.png?raw=true)

------

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/b67ff65b3d574025b65b6587266bbab7)](https://www.codacy.com/gh/alexpdev/torrentfile/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=alexpdev/torrentfile&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/b67ff65b3d574025b65b6587266bbab7)](https://www.codacy.com/gh/alexpdev/torrentfile/dashboard?utm_source=github.com&utm_medium=referral&utm_content=alexpdev/torrentfile&utm_campaign=Badge_Coverage)
![GitHub repo size](https://img.shields.io/github/repo-size/alexpdev/torrentfile)
![GitHub License](https://img.shields.io/github/license/alexpdev/torrentfile)
![PyPI - Downloads](https://img.shields.io/pypi/dw/torrentfile)
[![CI](https://github.com/alexpdev/TorrentFile/actions/workflows/pyworkflow.yml/badge.svg?branch=master&event=push)](https://github.com/alexpdev/torrentfile/actions/workflows/pyworkflow.yml)
[![DeepSource](https://deepsource.io/gh/alexpdev/TorrentFile.svg/?label=active+issues&token=16Sl_dF7nTU8YgPilcqhvHm8)](https://deepsource.io/gh/alexpdev/torrentfile/)

## :globe_with_meridians: Overview

A `simple` and `convenient` tool for creating, reviewing, editing, and/or  
checking/validating bittorrent meta files (aka torrent files). _`torrentfile`_  
supports all versions of Bittorrent files, including hybrid meta files.

> A GUI frontend for this project can be found at [https://github.com/alexpdev/TorrentfileQt](https://github.com/alexpdev/TorrentfileQt)

## :white_check_mark: Requirements

- Python 3.7+
- Tested on Linux and Windows

## :package: Install

__via PyPi:__

    pip install torrentfile

__via Git:__

    git clone https://github.com/alexpdev/torrentfile.git
    python setup.py install

> Download pre-compiled binaries from the [release page](https://github.com/alexpdev/torrentfile/releases).

## :scroll: Documentation

Documentation can be found  [here](https://alexpdev.github.io/torrentfile)
or in the _`docs`_ directory.

## :rocket: Usage

```bash
torrentfile [-h] [-i] [-V] [-v]  ...

Sub-Commands:

    create           Create a new torrent file.
    check            Check if file/folder contents match a torrent file.
    edit             Edit a pre-existing torrent file.
    magnet           Create Magnet URI for an existing torrent meta file.

optional arguments:
  -h, --help         show this help message and exit
  -V, --version      show program version and exit
  -i, --interactive  select program options interactively
  -v, --verbose      output debug information
```

> Usage examples can be found in the project documentation on the [examples page.](https://alexpdev.github.io/torrentfile/examples)

!!!
    _torrentfile_ is under active development, and is subject to significant changes in  
    it's codebase between releases.

## :memo: License

Distributed under the GNU LGPL v3. See `LICENSE` for more information.

## :bug: Issues

If you encounter any bugs or would like to request a new feature please open a new issue.

[https://github.com/alexpdev/torrentfile/issues](https://github.com/alexpdev/torrentfile/issues)

------

## CLI Usage Examples

Examples using TorrentFile with CLI arguments can be found below.
Alternatively, `interactive mode` allows program options to be specified
one option at a time  from a series of prompts using the following commands.

`torrentfile -i` or `torrentfile --interactive`

### Creating Torrents

Using the sub-command `create` _TorrentFile_ can create a new torrent
from the contents of a file or directory path. The following examples
illustrate some of the options available for creating torrent files.

- Create a torrent file from(`/path/to/content`) file or directory
- by default torrent files are saved to `/path/to/content.torrent`
- by default torrents are created using bittorrent meta version 1

```bash
> torrentfile create /path/to/content
```

- the `-t` or `--tracker` flag adds one or more items to the list of trackers

```bash
> torrentfile create /path/to/content --tracker http://tracker1.com
> torrentfile create /other/content -t http://tracker2 http://tracker3
```

- the `--private` flag indicates use by a private tracker
- the `--source` flag adds a "source" property and fills it

```bash
> torrentfile create ./content --source SrcStr --private
```

- to specify the save location use the `-o` or `--outfile` flags

```bash
> torrentfile create -o /specific/path/name.torrent ./content
```

- to create files using bittorrent v2 use `--meta-version 2`
- likewise `--meta-version 3` creates a hybrid torrent file.

```bash
> torrentfile create --meta-version 2 /path/to/content
> torrentfile create --meta-version 3 /path/to/content
```

- to create a magnet URI for the created torrent file use `--magnet`

```bash
> torrentfile create --t https://tracker1/annc https://tracker2/annc --magnet /path/to/content
```

### Check/Recheck Torrents

Using the sub-command `recheck` or `check` or `r` you can check how much of
a torrent's data you have available by comparing the contetnts to the original
torrent meta file.

- recheck torrent file `/path/to/name.torrent` with `./downloads/name`

```bash
> torrentfile recheck /path/to/name.torrent ./downloads/name
```

### Edit Torrents

Using the sub-command `edit` or `e` enables editting a pre-existing torrent file.
The edit sub-command works identically to the `create` sub-command and accepts many
of the same arguments.

### Create Magnet

To create a magnet URI for a pre-existing torrent meta file, use the sub-command  
`magnet` with the path to the meta file.

```bash
> torrentfile magnet /path/to/metafile
```
