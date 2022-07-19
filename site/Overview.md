# torrentfile Manual

## Synopsis

    torrentfile [options] <subcommand> [options] <args>

## Description

**`torrentfile`** is a command line toolkit for working with Bittorrent files(.torrent).
Some of the tools available include creating torrent files, editing portions of a
torrent file, checking the integrity or completeness of downloaded torrent contents,
displaying details of a torrentfile, generating magnet URLs for torrentfiles, and
individual or batch rebuilding of torrent contents into their original directory
structure.

### Options

- `-h`
displays all relevant command line options and subcommands.

- `-V`
displays program and version.

- `-v`
enables debug mode and outputs a large amount of information to the terminal.

- `-i`
activates interactive mode for selecting subcommands and options.

### Sub-commands

#### create

alias: `c`, `new`

    torrentfile create [options] <path>
    torrentfile c [options] <path>

The create subcommand is used for generating new torrent files. The only required
argument is the path(`<path>`) to the contents file or directory.

- `-a` `-t` `--announce` `--tracker`
Adds the list of url's that follow to the list of trackers for the newly created torrent file.
Example `-t http://url1 https://url2 ...`

- `-w` `--web-seeds`
Adds the list of urls that follow to the list of web-seed addresses for the newly created torrent file.

- `--comment`
Includes the comment that follows to the metadata saved in the newly created torrent file.
Example: `--comment "Created for MyTrackerExample.com"`

- `--source`
Creates a source field in the info dictionary with the string that follows as the value. Frequently used for
cross-seeding on private trackers.
Example: `--source MyTrackerExample`

- `-p` `--private`
Indicates that the torrent will be used on a private tracker. Disables multi-tracker protocols and DHT.

- `--piece-length`
Uses the number that follows as the piece-length size for the newly created torrent file. If option isn't used
the program will pick the ideal size. Acceptable values include 14-29 which is interpreted as the number to raise 2
by (e.g. 14 is interpreted as 16384), or any perfect power of 2 greater than or equal to 16 KiB and less than 1 GiB.
Example: `--piece-length 14` or `--piece-length 16384`.

- `--meta-version`
Use the following number as the Bittorrent version the torrent will be used on. The default is 1.
Options: 1 - Bittorrent v1,    2 - Bittorrent v2,    3 - Bittorrent v1 & v2
Examples: `--meta-version 1`, `--meta-version 2`, `--meta-version 3`

- `-o` `--out`
Specify the full path to the newly created torrent file.  The default is to save it adjacent to the content.
Example: if content is at `/home/user/torrents/content` the default would create `/home/user/torrents/content.torrent`

- `--cwd` `--current`
Changes the default save location to the current working directory.
Example: if content is at `/home/user/torrents/content` this option would create `./content.torrent`

- `--progress` `--prog`
Options (0, 1):  No status bar will be shown if 0.  Otherwise the default and 1 argument means progress bar is shown

#### info

alias: `i`

    torrentfile info <path>
    torrentfile i <path>

Display detailed information about a torrentfile such as trackers,
size of contents, Bittorrent version, any comments left, date the
torrent file was created and more. There is only one positional perameter
which is the path to the torrent file and there are no optional arguments.

- `/path/to/*.torrent`
The relative or absolute path to the torrent file.

#### edit

Edit some of the different information detailed in a torrent file. The fields that
are editable each have option flags detialed below. Each option identifies the
field to edit inside the torrent file and what the new value should be. If an
option is not used then its field will be ommited in the newly created torrent
file. As such if the file is marked as private and it should remain that way,
the `-p` option should be used.

alias: `e`

    torrentfile edit [options] <path>
    torrentfile e [options] <path>

- `-a` `-t` `--announce` `--tracker`
Adds the list of url's that follow to the list of trackers for the newly created torrent file.
Example `-t http://url1 https://url2 ...`

- `-w` `--web-seeds`
Adds the list of urls that follow to the list of web-seed addresses for the newly created torrent file.

- `--comment`
Includes the comment that follows to the metadata saved in the newly created torrent file.
Example: `--comment "Created for MyTrackerExample.com"`

- `--source`
Creates a source field in the info dictionary with the string that follows as the value. Frequently used for
cross-seeding on private trackers.
Example: `--source MyTrackerExample`

- `-p` `--private`
Indicates that the torrent will be used on a private tracker.  Disables multi-tracker protocols and DHT.

#### recheck

Recheck requires two paths as arguments. The first is the path to a torrent file, and
and the second is a path to the file of directory containing the downloaded data
from that torrentfile. `torrentfile` recursively validates each file with the hashes
contained in the torrentfile, and displays the amount missing frome each file, plus
a final percentage for the whole torrent at the conclusion. This will display a
progress bar for each file including missing files. It is also permitted to use
the contents parent directory which can help for batch processing many torrent files.

alias: `r`, `check`

    torrentfile recheck <*.torrent> <contents>
    torrentfile r <*.torrent> <contents>

### Magnet

Generate a magnet URL for a torrent file.

alias: `m`

    torrentfile magnet <path/to/*.torrent>

### Rebuild

Rebuild individual or batches of torrent contents into the original file structure.
The program takes a path to a torrent file or directory containing torrent files,
the directory containing the torrent contents, and the destination directory to
where the rebuilt torrent content wil be located. The program will recursively
traverse the content directory searching for file's that match one of the meta files
and creates copies of the matches to the destination directory. The original files
are not effected and any existing files in the target directory will not be
overwritten.

alias: `build`, `b`

    torrentfile rebuild <metafiles> <contents> <destination>
