# Name

- torrentfile

## Synopsis

    torrentfile [options] <subcommand> [optional] <args>

## Description

torrentfile is a tool for creating and/or manipulating Bittorrent files(.torrent).
It also provides tools for reviewing torrent file information, generating magnet links,
and checking/validating torrent content against its companion torrent file.

### Options

- `-h`
displays all relevant command line options and subcommands.

- `-V`
displays program and version.

- `-v`
enables verbose mode as well as a logfile.

- `-i`
activates interactive mode for selecting subcommands and options.

### Sub-commands

#### create

alias: `c`

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

- `--noprogress`
Turns off the progress bar indicator shown.

#### info

alias: `i`

    torrentfile info <path>
    torrentfile i <path>

There are no optional arguments for the info subcommand.

- `/path/to/*.torrent`
The relative or absolute path to the torrent file.

#### edit

alias: `e`

    torrentfile edit [options] <path>
    torrentfile e [options] <path>

Each option identifies the field to edit inside the torrent file and what the new value should be.
If an option is not used then its field will be ommited in the newly created torrent file. As such
if the file is marked as private and it should remain that way, the `-p` option should be used.

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

alias: `r`

    torrentfile recheck <path/to/*.torrent>  <path/to/contents>
    torrentfile r <path/to/*.torrent>  <path/to/contents>

There are only two arguments for the recheck command and both are mandatory.  The first is the absolute or relative
`<path>` to the torrent file, and the second is the absolute or relative `<path>` to it's content. This will display a
progress bar and at the end output what percent of the torrentfile's content it found at the path indicated. It is also
permitted to use the contents parent directory as the second argument and the result will be the same.
