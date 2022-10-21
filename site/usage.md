# TorrentFile CLI Menu

## Help Messages

### Main
    Usage
    =====
        torrentfile [options] command [command options]

    Command line tools for creating, editing, checking, building and interacting with Bittorrent metainfo files

    Options
    -------
        -h, --help             show this help message and exit
        -i, --interactive      select program options interactively
        -q, --quiet            Turn off all text output.
        -V, --version          show program version and exit
        -v, --verbose          output debug information

    Commands
    --------
    create, edit, info, magnet, recheck, rebuild

        create (c, new)      Create a new Bittorrent file.
        edit (e)             Edit existing torrent meta file.
        info (i)             Show detailed information about a torrent file.
        magnet (m)           Generate magnet url from an existing Bittorrent meta file.
        recheck (check)      Gives a detailed look at how much of the torrent is available.
        rebuild (build)      Re-assemble files obtained from a bittorrent file into the
                            appropriate file structure for re-seeding.  Read documentation
                            for more information, or use cases.

* * *

# Create

    Usage
    =====

        torrentfile [options] create
        [-h] [-a <url> [<url> ...]] [-p]
        [-s <source>] [-m] [-c <comment>]
        [-o <path>] [--cwd] [--prog PROGRESS]
        [--meta-version <int>]
        [--piece-length <int>]
        [-w <url> [<url> ...]]
        [--http-seed <url> [<url> ...]]
        [<content>]

    Positional Arguments
    --------------------
    <content>              Path to content file or directory

    Options
    -------
        -h, --help             show this help message and exit
        -a <url> [<url> ...], -t <url> [<url> ...], --announce <url> [<url> ...], --tracker <url> [<url> ...]
                            One or more space-seperated torrent tracker url(s).
        -p, --private          Creates private torrent with multi-tracker and DHT turned off.
        -s <source>, --source <source>
                            Add a source string. Useful for cross-seeding.
        -m, --magnet
        -c <comment>, --comment <comment>
                            Include a comment in file metadata
        -o <path>, --out <path>
                            Explicitly specify the path to write the file.
        --cwd, --current       *deprecated* Saving to current directory is default behaviour
        --prog PROGRESS, --progress PROGRESS
                            Set the progress bar level.
                            Options = 0, 1
                            (0) = Do not display progress bar.
                            (1) = Display progress bar.(default)

        --meta-version <int>   Bittorrent metafile version.
                            Options = 1, 2, 3
                            (1) = Bittorrent v1 (Default)
                            (2) = Bittorrent v2
                            (3) = Bittorrent v1 & v2 hybrid

        --piece-length <int>   (Default: <blank>) Number of bytes for per chunk of data transmitted
                            by Bittorrent client. Acceptable values include integers 14-26 which
                            will be interpreted as a perfect power of 2.  e.g. 14 = 16KiB pieces.
                            Examples:: [--piece-length 14] [--piece-length 20]

        -w <url> [<url> ...], --web-seed <url> [<url> ...]
                            list of web addresses where torrent data exists (GetRight).
        --http-seed <url> [<url> ...]
                            list of URLs, addresses where content can be found (Hoffman).

* * *

## Edit

    Usage
    =====
    torrentfile e [-h] [--tracker <url> [<url> ...]]
                        [--web-seed <url> [<url> ...]] [--private]
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

* * *

## Recheck

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

* * *

## Magnet

    Usage
    =====
    torrentfile m [-h] <*.torrent>

    Positional Arguments
    --------------------
    <*.torrent>  Path to Bittorrent meta file.

    Optional Arguments
    ------------------
    -h, --help   show this help message and exit

* * *
