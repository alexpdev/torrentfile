# TorrentFile

![torrentfile](https://github.com/alexpdev/torrentfile/blob/master/assets/torrentfile.png?raw=true)

------

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/202440df15224535b5358503e6235c88)](https://www.codacy.com/gh/alexpdev/TorrentFile/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=alexpdev/TorrentFile&amp;utm_campaign=Badge_Grade)
[![codecov](https://codecov.io/gh/alexpdev/TorrentFile/branch/master/graph/badge.svg?token=PXFsxXVAHW)](https://codecov.io/gh/alexpdev/TorrentFile)
![GitHub repo size](https://img.shields.io/github/repo-size/alexpdev/TorrentFile)
![GitHub License](https://img.shields.io/github/license/alexpdev/TorrentFile)
![PyPI - Downloads](https://img.shields.io/pypi/dw/torrentfile)
[![CI](https://github.com/alexpdev/TorrentFile/actions/workflows/python_workflow.yml/badge.svg?branch=master&event=push)](https://github.com/alexpdev/TorrentFile/actions/workflows/python_workflow.yml)
[![DeepSource](https://deepsource.io/gh/alexpdev/TorrentFile.svg/?label=active+issues&token=16Sl_dF7nTU8YgPilcqhvHm8)](https://deepsource.io/gh/alexpdev/TorrentFile/)

## Overview

A `simple` and `convenient` tool for creating, reviewing, editing, and  
checking/validating bittorrent meta files (aka torrent files). `torrentfile`  
support all versions of Bittorrent files, including hybrid meta files.

> A GUI frontend for this project can be found at [https://github.com/alexpdev/TorrentfileQt](https://github.com/alexpdev/TorrentfileQt)

## Requirements

- Python 3.7+
- Tested on Linux and Windows

## Install

### via PyPi

    pip install torrentfile

### via Git

    git clone https://github.com/alexpdev/torrentfile.git
    python setup.py install

> Or download pre-compiled binaries from the Github release page.
[https://github.com/alexpdev/torrentfile/releases](https://github.com/alexpdev/torrentfile/releases)

## Documentation

Documentation is available online at
[https://alexpdev.github.io/torrentfile](https://alexpdev.github.io/torrentfile)
 and in the `./docs` directory, or online at.

## :rocket: Usage

    ~$torrentfile -h

```bash
torrentfile [-h] [-i] [-V] [-v]  ...

Sub-Commands:

    create           Create a new torrent file.
    check            Check if file/folder contents match a torrent file.
    edit             Edit a pre-existing torrent file.

optional arguments:
  -V, --version      show program version and exit
  -h, --help         show this help message and exit
  -i, --interactive  select program options interactively
  -v, --verbose      output debug information
```

## License

Distributed under the GNU LGPL v3. See `LICENSE` for more information.

## Issues

If you encounter any bugs or would like to request a new feature please open a new issue.

[https://github.com/alexpdev/TorrentFile/issues](https://github.com/alexpdev/TorrentFile/issues)
