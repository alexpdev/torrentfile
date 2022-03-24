# TorrentFile

![torrentfile](https://github.com/alexpdev/torrentfile/blob/master/assets/torrentfile.png?raw=true)

------

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/b67ff65b3d574025b65b6587266bbab7)](https://www.codacy.com/gh/alexpdev/torrentfile/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=alexpdev/torrentfile&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/b67ff65b3d574025b65b6587266bbab7)](https://www.codacy.com/gh/alexpdev/torrentfile/dashboard?utm_source=github.com&utm_medium=referral&utm_content=alexpdev/torrentfile&utm_campaign=Badge_Coverage)
![GitHub repo size](https://img.shields.io/github/repo-size/alexpdev/torrentfile)
![GitHub License](https://img.shields.io/github/license/alexpdev/torrentfile)
![PyPI - Downloads](https://img.shields.io/pypi/dm/torrentfile)
[![codecov](https://codecov.io/gh/alexpdev/torrentfile/branch/master/graph/badge.svg?token=EWF7NIL9SQ)](https://codecov.io/gh/alexpdev/torrentfile)
[![CI](https://github.com/alexpdev/TorrentFile/actions/workflows/pyworkflow.yml/badge.svg?branch=master&event=push)](https://github.com/alexpdev/torrentfile/actions/workflows/pyworkflow.yml)
[![DeepSource](https://deepsource.io/gh/alexpdev/TorrentFile.svg/?label=active+issues&token=16Sl_dF7nTU8YgPilcqhvHm8)](https://deepsource.io/gh/alexpdev/torrentfile/)

## 🌐 Overview

A `simple` and `convenient` tool for creating, reviewing, editing, and/or
validating bittorrent meta files (aka torrent files). _`torrentfile`_
supports all versions of Bittorrent files, including hybrid meta files, and has
full unicode support.

> A GUI frontend for this project can be found at [https://github.com/alexpdev/TorrentfileQt](https://github.com/alexpdev/TorrentfileQt)

## 🔌 Requirements

- Python 3.7+
- Tested on Linux and Windows and Mac

## 💻 Install

__via PyPi:__

```bash
pip install torrentfile
```

__via Git:__

```bash
git clone https://github.com/alexpdev/torrentfile.git
cd torrentfile
python setup.py install
```

> Download pre-compiled binaries from the [release page](https://github.com/alexpdev/torrentfile/releases).

## 📚 Documentation

Documentation can be found  [here](https://alexpdev.github.io/torrentfile)
or in the _`docs`_ directory.

>_torrentfile_ is under active development, and is subject to significant changes in  
    it's codebase between releases.

## 🚀 Usage

```sh
Usage
=====
   torrentfile [-h] [-i] [-V] [-v]
                   <create> <edit> <magnet> <recheck> ...

CLI Tool for creating, checking, editing... Bittorrent meta files. TorrentFile supports all versions of torrent files.

Options
-------
  -h, --help                          show this help message and exit
  -i, --interactive                   select program options interactively
  -V, --version                       show program version and exit
  -v, --verbose                       output debug information

Actions
-------
  <create> <edit> <magnet> <recheck>
    c (create, new)                   Create a torrent meta file.

    e (edit)                          Edit existing torrent meta file.

    m (magnet)                        Create magnet url from an existing Bittorrent meta file.

    r (recheck, check)                Calculate amount of torrent meta files content is found on disk.

    i (info)                          Show detailed information about a torrent file.
```

> Usage examples can be found in the project documentation on the [examples page.](https://alexpdev.github.io/torrentfile/examples)

## 📝 License

Distributed under the GNU LGPL v3. See `LICENSE` for more information.

## 💡 Issues

If you encounter any bugs or would like to request a new feature please open a new issue.

[https://github.com/alexpdev/torrentfile/issues](https://github.com/alexpdev/torrentfile/issues)

------

## ⚙️ CLI Usage Examples

> More examples can be found in the documentation.

### Creating Torrents

Using the sub-command `create` or `c` _TorrentFile_ can create a new torrent  
from the contents of a file or directory path. The following examples illustrate  
some of the options available for creating torrents (AKA meta files).

- Create a torrent from any file or directory. example (`/path/to/content`)
- by default the save path will be the content path with a ".torrent" extension. (`/path/to/content.torrent`)
- by default torrents are created using bittorrent meta-version 1

```bash
torrentfile create /path/to/content
```

- The `-t` or `--tracker` flag adds one or more urls to tracker list.
- This flag will cause an error if the content path immediately follows it.

do this

```bash
torrentfile create /path/to/content --tracker http://tracker1.com
```

or this

```bash
torrentfile create -t http://tracker2 http://tracker3 --private /path/to/content
```

not this

```bash
torrentfile create --tracker http://tracker /path/to/content   #ERROR
torrentfile create -t http://tracker1 http://tracker2 /path/to/content #ERROR
```

- the `--private` flag indicates use by a private tracker
- the `--source` flag can be used to help with cross-seeding

```bash
torrentfile create --private --source /path/to/content --tracker https://tracker/url
```

- to turn off the progress bar shown use `--noprogress`
- this can improve the performance by a very small amount

```bash
torrentfile -t <url1> <url2> --noprogress ./content
```

- to specify the save location use the `-o` or `--out` flags

```bash
torrentfile create -o /specific/path/name.torrent ./content
```

- to create files using bittorrent v2 use `--meta-version 2`
- likewise `--meta-version 3` creates a hybrid torrent file.

```bash
torrentfile create --meta-version 2 /path/to/content
torrentfile create --meta-version 3 /path/to/content
```

- to output a magnet URI for the created torrent file use `--magnet`

```bash
torrentfile create --t https://tracker1/annc https://tracker2/annc --magnet /path/to/content
```

### Check/Recheck Torrent

Using the sub-command `recheck` or `check` or `r` you can check the percentage of a torrent  
is saved to disk by comparing the the contents to a torrent metafile.

- recheck torrent file `/path/to/some.torrent` with `/path/to/content`
- enter the metafile path first then the content path (the order matters)

```bash
torrentfile recheck /path/to/some.torrent /path/to/content
```

### Edit Torrent

Using the sub-command `edit` or `e` enables editting a pre-existing torrent file.
The edit sub-command works the same as the `create` sub-command and accepts many
of the same arguments.

### Create Magnet

To create a magnet URI for a pre-existing torrent meta file, use the sub-command  
`magnet` or `m` with the path to the torrent file.

```bash
torrentfile magnet /path/to/some.torrent
```

### Torrent Details

If you are just trying to get the details of a particular torrent file, such as  
the trackers it has been assigned, or the number of files it contains, use `info` or `i`.

```bash
torrentfile info /path/to/some.torrent
```

#### Interactive Mode

Alternatively to supplying a bunch of command line arguments, `interactive mode`
allows users to specify program options one at a time from a series of prompts.

- to activate interactive mode use `-i` or `--interactive` flag

```bash
torrentfile -i
```
