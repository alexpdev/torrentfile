# TorrentFile

![torrentfile](https://github.com/alexpdev/torrentfile/blob/master/assets/torrentfile.png?raw=true)

------

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/2da47ec1b5904538a40230f049a02be4)](https://www.codacy.com/gh/alexpdev/torrentfile/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=alexpdev/torrentfile&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/2da47ec1b5904538a40230f049a02be4)](https://www.codacy.com/gh/alexpdev/torrentfile/dashboard?utm_source=github.com&utm_medium=referral&utm_content=alexpdev/torrentfile&utm_campaign=Badge_Coverage)
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
