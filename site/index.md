# TorrentFile

![torrentfile](https://github.com/alexpdev/torrentfile/blob/master/site/images/torrentfile.png?raw=true)

------

![GitHub repo size](https://img.shields.io/github/repo-size/alexpdev/torrentfile?color=orange)
![GitHub License](https://img.shields.io/github/license/alexpdev/torrentfile?color=red&logo=apache)
![PyPI - Downloads](https://img.shields.io/pypi/dm/torrentfile?color=brown)
[![CI](https://github.com/alexpdev/TorrentFile/actions/workflows/pyworkflow.yml/badge.svg?branch=master&event=push)](https://github.com/alexpdev/torrentfile/actions/workflows/pyworkflow.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/b67ff65b3d574025b65b6587266bbab7)](https://www.codacy.com/gh/alexpdev/torrentfile/dashboard?utm_source=github.com&utm_medium=referral&utm_content=alexpdev/torrentfile&utm_campaign=Badge_Coverage)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/b67ff65b3d574025b65b6587266bbab7)](https://www.codacy.com/gh/alexpdev/torrentfile/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=alexpdev/torrentfile&amp;utm_campaign=Badge_Grade)
[![DeepSource](https://deepsource.io/gh/alexpdev/TorrentFile.svg/?label=active+issues&token=16Sl_dF7nTU8YgPilcqhvHm8)](https://deepsource.io/gh/alexpdev/torrentfile/)
[![codecov](https://codecov.io/gh/alexpdev/torrentfile/branch/master/graph/badge.svg?token=EWF7NIL9SQ)](https://codecov.io/gh/alexpdev/torrentfile?color=navy&logo=codecov)

## 🌐 Overview

A `simple` and `convenient` tool for creating, reviewing, editing, and/or
validating bittorrent meta files (aka torrent files). _`torrentfile`_
supports all versions of Bittorrent files, including hybrid meta files, and has
full unicode support.

> A GUI frontend for this project can be found at [https://github.com/alexpdev/TorrentfileQt](https://github.com/alexpdev/TorrentfileQt)

## 🔌 Requirements

- Python 3.7+
- Tested on Linux, Windows and Mac

## 💻 Install

__via PyPi:__

```bash
pip install torrentfile
```

__via Git:__

```bash
git clone https://github.com/alexpdev/torrentfile.git
cd torrentfile
pip install .
```

> Download pre-compiled binaries from the [release page](https://github.com/alexpdev/torrentfile/releases).

## 📚 Documentation

Documentation can be found  [here](https://alexpdev.github.io/torrentfile)
or in the _`docs`_ directory.

>_torrentfile_ is under active development, and is subject to significant changes in the codebase between releases.

## 🚀 Usage

![Basic Usage](https://github.com/alexpdev/torrentfile/blob/master/assets/TorrentFileBasicUsage.gif?raw=True)

```bash
Usage
=====
   torrentfile [-h] [-i] [-V] [-v]
                   create, edit, magnet,
                   recheck, rebuild ...

Command line tools for creating, editing, checking and interacting with Bittorrent metainfo files

Options
-------
  -h, --help             show this help message and exit
  -i, --interactive      select program options interactively
  -V, --version          show program version and exit
  -v, --verbose          output debug information

Actions
-------
  create, edit, magnet, recheck, rebuild

    create (c, new)      Generate a new torrent meta file.
    edit (e)             Edit existing torrent meta file.

    magnet (m)           Generate magnet url from an existing Bittorrent meta file.

    recheck (r, check)   Calculate amount of torrent meta files content is found on disk.

    info (i)             Show detailed information about a torrent file.

    rebuild (build, b)   Re-assemble files obtained from a bittorrent file into the
                         appropriate file structure for re-seeding.  Read documentation
                         for more information, or use cases.
```

> Usage examples can be found in the project documentation on the [examples page.](https://alexpdev.github.io/torrentfile/examples)

## 📝 License

Distributed under Apache v2 software license. See `LICENSE` for more information.

## 💡 Issues & Requests & PRs

If you encounter any bugs or would like to request a new feature please open a new issue.

> PRs and other contributions are welcome

[https://github.com/alexpdev/torrentfile/issues](https://github.com/alexpdev/torrentfile/issues)

------

### Creating Torrents

- Basic torrent file createion

```bash
> torrentfile create /path/to/content
```

- The `-t` `--tracker` `-a` `--announce` flags add one or more urls to list of trackers.

```bash
> torrentfile create /path/to/content --tracker http://tracker1.com

> torrentfile create -t http://tracker2 http://tracker3 --private /path/to/content

> torrentfile create --tracker http://tracker /path/to/content  

> torrentfile create -t http://tracker1 http://tracker2 /path/to/content
```

- the `--private` flag indicates use by a private tracker
- the `--source` flag can be used to help with cross-seeding

```bash
> torrentfile create --private --source EXAMPLE --tracker https://url1 https://url2
```

The options for controlling the progress bar using `--prog` or `--progress`:

- 0 : show no progress bar at all
- 1 : show progress bar (default)

```bash
> torrentfile create -t http://tracker.com --progress 2 /path/to/content
> torrentfile create --prog 0 /path/to/content
```

- to specify the save location use the `-o` or `--out` flags
- if the path points to directory the name of torrent is autofilled.

```bash
> torrentfile create -o /specific/path/name.torrent ./content
```

- to create files using bittorrent v2 use `--meta-version 2`
- likewise `--meta-version 3` creates a hybrid torrent file.

```bash
> torrentfile create --meta-version 2 /path/to/content
> torrentfile create --meta-version 3 /path/to/content
```

### Check/Recheck Torrent

- recheck torrent file `/path/to/some.torrent` with `/path/to/content`

```bash
> torrentfile recheck /path/to/some.torrent /path/to/content
```

### Edit Torrent

- edit a torrent file

```bash
> torrentfile edit [options] <path>
```

### Create Magnet

To create a magnet URI for a pre-existing torrent meta file, use the sub-command  
`magnet` or `m` with the path to the torrent file.

```bash
> torrentfile magnet /path/to/some.torrent
```

#### Interactive Mode (expiremental)

Alternatively to supplying a bunch of command line arguments, `interactive mode`
allows users to specify program options one at a time from a series of prompts.

- to activate interactive mode use `-i` or `--interactive` flag

```bash
> torrentfile -i
```

### GUI

If you prefer a windowed gui please check out the official GUI frontend [here](https://github.com/alexpdev/TorrentFileQt)
