# TorrentFile

## Version 0.6.13

- Fixed bug that created a torrent file with no name.
- Fixed bug that would error if cli path was listed after announce urls
- Added full unicode support.
- Added Unittests for new features and bug fixes

---------------------

## Version 0.6.11

- Fixed bug that occured during recheck when file of 0 length is included.
- Altered Recheck algorithm to process 0 length files.
- Only effected meta version 2 and hybrid torrent files.
- Added unittests to cover the situation.

---------------------

## Version 0.6.10

- Updates to documentation
- Integrated Type hints in source code
- Updated build and CI process

---------------------

## Version 0.6.9

- The --progress flag is now --noprogress
- Default behavior is to show progress bar
- use --noprogress to not show
- added CLI Help format strings
- added custom CLI help formatter class
- Titled Help Message section headers
- Fixed a bunch of error pages created by mkdocs

---------------------

## Version 0.6.8

- Documentation for newest features
- CLI usage examples
- Improved unittests
- made progress bar active by default

---------------------

## Version 0.6.7

- Updates to API

---------------------

## Version 0.6.6

- bug that created faulty Bittorrent V2 meta files in some instances.
- back to working as it should.

---------------------

## Version 0.6.5

- Support for creating Magnet URI's
- Added optional progress bar for torrent creation
- Log File handler
- CLI args page in documentation
- verbose and logging bugs
- multi tracker errors bug

---------------------

## Version 0.6.4

- CLI interface add subcommands
- added interactive mode
- Re-wrote the recheck module
- fixed documentation and docstrings
- linting and testing errors

---------------------

## Version 0.6.3

- Fixed Bug that would format list of trackers incorrectly
- CLI Bug Fixes

---------------------

## Version 0.6.2

- Bug fixes
- Documentation error pages

---------------------

## Version 0.6.0

- cli commands alterations
- debug logging during creation process

---------------------

## Version 0.5.2

- Fixed Bug that was adding wrong fields to info dict

---------------------

## Version 0.5.0

- Slew of new unit tests
- Stricter linting features
- Alternative method of -re-check feature
- Bug Fixes
- CLI help formatting errors

---------------------

## Version 0.4.8

- Improved Algorithm performance for ReCheck.
- Additions to documentation.

---------------------

## Version 0.4.7

- Fixed A bug that misspelled a field when creating Hybrid torrent files.
- Re-Check procedure for v2 and hybrid torrent file checking.

---------------------

## Version 0.4.6

- CLI Help and Usage Messages.
- Expanded CLI args.
- Completely new CheckerClass which replaces old Checker
- Hooks for GUI or other 3rd party apps to hook into Checking
- Documentation and Unit tests for new CheckerClass

---------------------

## Version 0.4.5

- Documentation and docstrings improvements
- Better code formating and more detailed docstrings
- More unit tests.

---------------------

## Version 0.4.2

- The ReChecker feature now supports v1, v2, & hybrid .torrent file.
- Bug in CLI for python < 3.8

---------------------

## Version 0.4.1

- Added tests for hybrid class
- Added logging features
- new cli flag to activate debug mode
- Documentation theme.
- Fixed Bug that allowed improper piece length values.

---------------------

## Version 0.4.0

- Fixed bugs in creating hybrid files.
- Bug Fix that broke cli.

---------------------

## Version 0.3.0

- Added/Improved support for hybrid meta files.
- Many additions to testing suit including linting and coverage tests.

---------------------

## Version 0.2.8

- Styling fixes.
- Bug Fixes.
- Prelimenary support for bittorrent hybrid meta files.
- Bug Fixes

---------------------

## Version 0.2.7

- major imporvements to torrentfile-GUI.
- minor adjustments to this package for integration.
- Code consolidation
- Bug Fixes
- Documentation additions
- Implemented CI/CD Integration

---------------------

## Version 0.2.3

- Bug Fixes
- Code Style and Formatting
- Added more unittests

---------------------

## Version 0.2.1

- Bittorrent Protocol V2 Support
- v2 metafile options to cli
- v2 metafile tests

---------------------

## Version 0.1.7

- Docstrings Improvements.
- Added documentation rederer.
- Improved readme file.
- formatting

---------------------

## Version 0.1.2

- Added a Command Line Interface
- Rough Graphical User Interface
- Minor Bug Fixes
- Improved unittest coverage

---------------------

## Version 0.1.0

- added SHA256 support
- Feeder class for seemless file switching
- Fixed the primary entrypoint function.
- Improved docstrings
- Bug fixes

---------------------

## Version 0.0.2

- Added Unittests
- added bencode support
- added hashing support

---------------------

## Version 0.0.1

- Initial concept and planning
