# TorrentFile CLI Menu

## Help Messages

```bash:
Usage
=====
   torrentfile [-h]  [-i]  [-V]  [-v]
                   <create> <edit> <magnet> <recheck> ...

CLI utility for editing, creating, checking, and other useful tools for Bittorrent meta files. 
TorrentFile supports all versions of torrent files.

Optional Arguments
------------------
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

    r (recheck, check)                Calculate amount of torrent meta file's content is found on disk.
```

-----

## create

```bash:
Usage
=====
   torrentfile c [-h] [-a <url> [<url> ...]] [-p] [-s <source>] [-m]
                     [-c <comment>] [-o <path>] [-t <url> [<url> ...]]
                     [--noprogress] [--meta-version <int>] [--private]
                     [--piece-length <int>] [-w <url> [<url> ...]]
                     <content>

Positional Arguments
--------------------
  <content>                                           Path to content file or directory

Optional Arguments
------------------
  -h, --help                                          show this help message and exit
  -a <url> [<url> ...], --announce <url> [<url> ...]  Alias for -t/--tracker
  -p, --private                                       Create a private torrent file
  -s <source>, --source <source>                      Useful for cross-seeding
  -m, --magnet                                        Output Magnet Link after creation completes
  -c <comment>, --comment <comment>                   Include a comment in file metadata
  -o <path>, --out <path>                             Output path for created .torrent file
  -t <url> [<url> ...], --tracker <url> [<url> ...]   One or more Bittorrent tracker announce url(s).
  --noprogress                                        Disable showing the progress bar during torrent creation.
                                                      (Minimially improves performance of torrent file creation.)
  --meta-version <int>                                Bittorrent metafile version.
                                                      Options - {1, 2, 3}
                                                      (1) = Bittorrent v1 (Default)
                                                      (2) = Bittorrent v2
                                                      (3) = Bittorrent v1 & v2 hybrid
  --piece-length <int>                                Number of bytes per piece. (Default: None)
                                                      Acceptable inputs include {14 - 24} as exponent for 2^n,
                                                      or any acceptable integer value (must be power of 2).
                                                      Examples:: [--piece-length 14] [--piece-length 16777216]
  -w <url> [<url> ...], --web-seed <url> [<url> ...]  One or more url(s) linking to a http server hosting
                                                      the torrent contents.  This is useful if the torrent
                                                      tracker is ever unreachable. Example:: -w url1 url2 url3
```

-----

## edit

```bash:
Usage
=====
   torrentfile e [-h] [--tracker <url> [<url> ...]]
                     [--web-seed <url> [<url> ...]]  [--private]
                     [--comment <comment>] [--source <source>]
                     <*.torrent>

Positional Arguments
--------------------
  <*.torrent>                   path to *.torrent file

Optional Arguments
------------------
  -h, --help                    show this help message and exit
  --tracker <url> [<url> ...]   Replace current list of tracker/announce urls with one or more space
                                seperated Bittorrent tracker announce url(s).

  --web-seed <url> [<url> ...]  Replace current list of web-seed urls with one or more space seperated url(s)

  --private                     Make torrent private.
  --comment <comment>           Replaces any existing comment with <comment>
  --source <source>             Replaces current source with <source>
```

-----

## Recheck

```bash
Usage
=====
   torrentfile r [-h] <*.torrent> <content>

Positional Arguments
--------------------
  <*.torrent>  path to .torrent file.
  <content>    path to content file or directory

Optional Arguments
------------------
  -h, --help   show this help message and exit
```

-----

## magnet

```bash:
Usage
=====
   torrentfile m [-h] <*.torrent>

Positional Arguments
--------------------
  <*.torrent>  Path to Bittorrent meta file.

Optional Arguments
------------------
  -h, --help   show this help message and exit
```
