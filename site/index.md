# TorrentFile

![torrentfile](https://github.com/alexpdev/torrentfile/blob/master/site/images/torrentfile.png?raw=true)

* * *

![GitHub repo size](https://img.shields.io/github/repo-size/alexpdev/torrentfile?color=orange)
![GitHub License](https://img.shields.io/github/license/alexpdev/torrentfile?color=red&logo=apache)
![PyPI - Downloads](https://img.shields.io/pypi/dm/torrentfile?color=brown)
![GitHub Last Commit](https://badgen.net/github/last-commit/alexpdev/torrentfile?color=blue&icon=github)
[![CI](https://github.com/alexpdev/TorrentFile/actions/workflows/pyworkflow.yml/badge.svg?branch=master&event=push)](https://github.com/alexpdev/torrentfile/actions/workflows/pyworkflow.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/b67ff65b3d574025b65b6587266bbab7)](https://www.codacy.com/gh/alexpdev/torrentfile/dashboard?utm_source=github.com&utm_medium=referral&utm_content=alexpdev/torrentfile&utm_campaign=Badge_Coverage)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/b67ff65b3d574025b65b6587266bbab7)](https://www.codacy.com/gh/alexpdev/torrentfile/dashboard?utm_source=github.com&utm_medium=referral&utm_content=alexpdev/torrentfile&utm_campaign=Badge_Grade)
[![DeepSource](https://deepsource.io/gh/alexpdev/TorrentFile.svg/?label=active+issues&token=16Sl_dF7nTU8YgPilcqhvHm8)](https://deepsource.io/gh/alexpdev/torrentfile/)
[![codecov](https://codecov.io/gh/alexpdev/torrentfile/branch/master/graph/badge.svg?token=EWF7NIL9SQ)](https://codecov.io/gh/alexpdev/torrentfile?color=navy&logo=codecov)

## 🌐 Overview

A `simple` and `convenient` tool for creating, reviewing, editing, and/or
validating bittorrent meta files (aka torrent files). _`torrentfile`_
supports all versions of Bittorrent files, including hybrid meta files, and has
full unicode support.

> A GUI frontend for this project can be found at <https://github.com/alexpdev/TorrentfileQt>

## 🔌 Requirements

-   Python 3.6+
-   Tested on Linux, Windows and Mac

## 💻 Install

**via PyPi:**

```bash
pip install torrentfile
```

**via Git:**

```bash
git clone https://github.com/alexpdev/torrentfile.git
cd torrentfile
pip install .
```

> Download pre-compiled binaries from the [release page](https://github.com/alexpdev/torrentfile/releases).

## 📚 Documentation

Documentation can be found  [here](https://alexpdev.github.io/torrentfile)
or in the _`docs`_ directory.

> _torrentfile_ is under active development, and is subject to significant changes in the codebase between releases.

## 🚀 Usage

![Basic Usage](https://github.com/alexpdev/torrentfile/blob/master/assets/TorrentFileBasicUsage.gif?raw=True)

> Usage examples can be found in the project documentation on the [examples page.](https://alexpdev.github.io/torrentfile/usage)

## 📝 License

Apache Software License v2.0 - See [LICENSE]("https://github.com/alexpdev/torrentfile/blob/master/LICENSE")

## 💡 Issues & Requests & PRs

If you encounter any bugs or would like to request a new feature please open a new issue.

> PRs and other contributions are welcome

<https://github.com/alexpdev/torrentfile/issues>

* * *

## Usage Examples

### Creating Bittorrent Files

Basic torrent file creation is as easy and using the `create` sub-commnand and providing  
the path to the contents.

```bash
torrentfile create /path/to/content
```

You can add one or more trackers by using any one of `-t`, `--tracker`, `-a`, `--announce` 
flags and listing their URL as a space separated list.

```bash
torrentfile create /path/to/content -a http://tracker1.com http://tracker2.net
```

If you intend to distribute the file on a private tracker then you should use one  
of `-p`, `--private` flags, which tells your Bittorrent clients to disable DHT and  
multitracker protocols.

```bash
torrentfile create /path/to/content --private
```

By default **`torrentfile`** displays a progress bar indicating how much of the content  
has already been processed.  To turn off this display you can either use `--quiet` mode in  
as a global flag or you can set the `--prog` flag to 0.

```bash
torrentfile --quiet create /path/to/content
```

```bash
torrentfile create /path/to/content --prog 0
```

**`torrentfile`** automatically extracts the name of the file or directory  
if the content and saves the file to the current working directory with the 
extracted title.

For example running the follwing command would create `./content.torrent`.

```bash
torrentfile create /path/to/content
```

To specify an alternative path or filename you may use the `-o`, `--out` flags  
followed by the relative or absolute path to your preferred output location.

```bash
torrentfile create /path/to/content -o /some/other/path/torrent.torrent
```

If the path you specified with the `-o` flag already exists and is a directory,  
then torrentfile will save the output to that directory with the default extracted title.

For example the following command would create a Bittorrent file at `/some/other/path/content.torrent`.

```bash
torrentfile create /path/to/content -o /some/other/path/
```

Bittorrent V1 is still the most common version of torrent files and the most widely accepted,  
therefore by default torrentfile uses the version 1 format.  However if you are using a modern 
Bittorrent client and tracker then you may wish to use the newest version Bittorrent V2 or 
a combination of the two.  To do this simply use the `--meta-version` flag with the appropriate  
version.  Options include `1`(v1 default), `2`(v2), or `3`(v1 & v2).

```bash
torrentfile create /path/to/content --meta-version 2
```

```bash
torrentfile create /path/to/content --meta-version 3 
```

### Check/Recheck Torrent

The `recheck` subcommand allows you to scan a Bittorrent file and compare it's contents, 
against a file or directory containing the contents the torrent file was created from.
The output provided by this process gives a detailed perspective if any files are missing
or have been corrupted in any way.  Supports any version of Bittorrent file.

```bash
torrentfile recheck /path/to/some.torrent /path/to/content
```

### Edit Torrent

To edit specific fields of the torrent file, there is the `edit` subcommand.  Using this
subcommand you can specify the field with one of the available field flags, for example
`--tracker` and specify the value you wish to change it to.

```bash
torrentfile edit /path/to/content --tracker https://new.tracker.url1.com  https://newtracker.url/2
```

You can use the `-h` flag for a full list of available fields that can be edited.

    torrentfile edit -h

### Create Magnet

To create a magnet URI for a pre-existing torrent meta file, use the sub-command  
`magnet` or `m` with the path to the torrent file.

```bash
torrentfile magnet /path/to/some.torrent
```

### GUI

If you prefer a windowed GUI please check out the official GUI frontend [here](https://github.com/alexpdev/TorrentFileQt)
