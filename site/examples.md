# TorrentFile

## CLI Usage Examples

Examples using TorrentFile with CLI arguments can be found below.
Alternatively, `interactive mode` allows program options to be specified
one option at a time  from a series of prompts using the following commands.

`torrentfile -i` or `torrentfile --interactive`

### Creating Torrents

Using the sub-command `create` _TorrentFile_ can create a new torrent
from the contents of a file or directory path. The following examples
illustrate some of the options available for creating torrent files.

- Create a torrent file from(`/path/to/content`) file or directory
- by default torrent files are saved to `/path/to/content.torrent`
- by default torrents are created using bittorrent meta version 1

```bash
> torrentfile create /path/to/content
```

- the `-t` or `--tracker` flag adds one or more items to the list of trackers

```bash
> torrentfile create /path/to/content --tracker http://tracker1.com
> torrentfile create /other/content -t http://tracker2 http://tracker3
```

- the `--private` flag indicates use by a private tracker
- the `--source` flag adds a "source" property and fills it

```bash
> torrentfile create ./content --source TrackerReq --private
```

- to specify the save location use the `-o` or `--outfile` flags

```bash
> torrentfile create ./content -o /specific/path/name.torrent
```

- to create files using bittorrent v2 or other formats use `--meta-version`
- `--meta-version 3` asks for a v1 & v2 hybrid file.

```bash
> torrentfile create /path/to/content --meta-version 2 -t https://tracker1.com
> torrentfile create /path/to/content --meta-version 3 
```

### Recheck Torrents

Using the sub-command `recheck` or `check` or `r` you can check how much of
a torrents data you have saved by comparing the contetnts to the original
torrent file.

- recheck torrent file `/path/to/name.torrent` with `./downloads/name`

```bash
> torrentfile recheck /path/to/name.torrent ./downloads/name
```

### Edit Torrents

Using the sub-command `edit` or `e` enables editting a pre-existing torrent file.
The edit sub-command works identically to the `create` sub-command and accepts many
of the same arguments.
