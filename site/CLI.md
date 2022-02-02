# TorrentFile CLI Menu

## Help Message

```bash:
usage: TorrentFile [-h] [-i] [-V] [-v]
                {c,create,new,e,edit,m,magnet,r,recheck,check} ...

CLI Tool for creating, checking and editing Bittorrent meta files. Supports all meta file versions including hybrid files.

optional arguments:
-h, --help                                      show this help message and exit
-i, --interactive                               select program options interactively
-V, --version                                   show program version and exit
-v, --verbose                                   output debug information

Actions:
Each sub-command triggers a specific action.

{c,create,new,e,edit,m,magnet,r,recheck,check}
    c (create, new)                               Create a torrent meta file.

    e (edit)                                      Edit existing torrent meta file.

    m (magnet)                                    Create magnet url from an existing Bittorrent meta file.

    r (recheck, check)                            Calculate amount of torrent meta file's content is found on disk.
```

-----

## create

```bash:
usage: TorrentFile c [-h] [-a <url> [<url> ...]] [-p] [-s <source>] [-m]
                    [-c <comment>] [-o <path>] [-t <url> [<url> ...]]
                    [--progress] [--meta-version <int>]
                    [--piece-length <int>] [-w <url> [<url> ...]]
                    <content>

positional arguments:
<content>                                           path to content file or directory

optional arguments:
-h, --help                                          show this help message and exit
-a <url> [<url> ...], --announce <url> [<url> ...]  Alias for -t/--tracker
-p, --private                                       Create a private torrent meta file
-s <source>, --source <source>                      specify source tracker
-m, --magnet                                        output Magnet Link after creation completes
-c <comment>, --comment <comment>                   include a comment in file metadata
-o <path>, --out <path>                             Output path for created .torrent file
-t <url> [<url> ...], --tracker <url> [<url> ...]   One or more Bittorrent tracker announce url(s).
--progress                                          Enable showing the progress bar during torrent creation.
                                                    (Minimially impacts the duration of torrent file creation.)

--meta-version <int>                                Bittorrent metafile version.
                                                    Options = 1, 2 or 3.
                                                    (1) = Bittorrent v1 (Default)
                                                    (2) = Bittorrent v2
                                                    (3) = Bittorrent v1 & v2 hybrid

--piece-length <int>                                Fixed amount of bytes for each chunk of data. (Default: None)
                                                    Acceptable input values include integers 14-24, which
                                                    will be interpreted as the exponent for 2^n, or any perfect
                                                    power of two integer between 16Kib and 16MiB (inclusive).
                                                    Examples:: [--piece-length 14] [-l 20] [-l 16777216]

-w <url> [<url> ...], --web-seed <url> [<url> ...]  One or more url(s) linking to a http server hosting
                                                    the torrent contents.  This is useful if the torrent
                                                    tracker is ever unreachable. Example:: [-w url1 [url2 [url3]]]
```

-----

## edit

```bash:
usage: TorrentFile e [-h] [--tracker <url> [<url> ...]]
                    [--web-seed <url> [<url> ...]] [--private]
                    [--comment <comment>] [--source <source>]
                    <*.torrent>

positional arguments:
<*.torrent>                   path to *.torrent file

optional arguments:
-h, --help                    show this help message and exit
--tracker <url> [<url> ...]   replace current list of tracker/announce urls with one or more space
                                seperated Bittorrent tracker announce url(s).

--web-seed <url> [<url> ...]  replace current list of web-seed urls with one or more space seperated url(s)

--private                     If currently private, will make it public, if public then private.
--comment <comment>           replaces any existing comment with <comment>
--source <source>             replaces current source with <source>
```

-----

## magnet

```bash:
usage: TorrentFile m [-h] <*.torrent>

positional arguments:
<*.torrent>  path to Bittorrent meta file.

optional arguments:
-h, --help   show this help message and exit
usage: TorrentFile r [-h] <*.torrent> content
```
