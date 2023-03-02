# TorrentFile

## Version 0.8.8

- added loading create torrent options from a configuration file
- added unit tests for configuration functions
- update documentation with new information about configuration file
- added CLI options for indicating the use of a configuration file `--config`
- added a CLI option that specifies where to look for config file  `--config-path`
- removed interactive `-i` mode from cli options as it is now deprecated.

---

## Version 0.8.7

- Added the rename subcommand
- Added unittests for the new subcommand
- Default command is now "create" when user ommits entering subcommand
- Added unittests for default command
- Added shortcut command `tfile` as an alternative to `torrentfile`

---

## Version 0.8.6

- Fixed bug with argument parser that allowed for duplicate aliases
- Added support for python 3.11
- Updated CI/CD Workflow
- Updated documentation
- Deprecated the -i interactive argument option and added warnings in documentation

---

## Version 0.8.5

- Fixed bug with linux platforms not installing a binary cli command
- Fixed debug logging errors with the rebuild command
- Improved log message readability
- Compatability upgrades for torrentfileQt synchronization
- Added coverage details to documentation folder

---

## Version 0.8.4

- Documentation Updates
- Fixed logging issues with rebuild module.
- Improved algorithm for rebuild module.
- Improved testing for rebuild module.

---

## Version 0.8.3

- Added the callback mixin to the rebuild module
- Fix compatability with GUI frontend torrentfileQt.

---

## Version 0.8.2

- Rebuild subcommand now checks on a hash by hash basis
- Fixed coverage issues
- Added unittests for the rebuild command
- Fixed bug with torrentfile creation when a file was a perfect power of 2
- Reconfigured the rebuild module
- Reconfigured the rebuild cli flags and arguments

---

## Version 0.8.1

- Further improvements to documentation
- Fixed bug that interrupted the creation process when using gui version
- Added unittests
- Improved docstrings and docstring formatting
- Renamed a couple of methods

---

## Version 0.8.0

- overhaul documentation
- reconfigured CI files and configuration and packaging files
- Convert to pyproject.toml setuptools packaging info source

---

## Version 0.7.12

- Changed default behavior to save torrent files to cwd
- edited all unittests to reflect default behavior
- added deprecation messages for the cli arg and class paramteter
- last update to version 0.7.x

---

## Version 0.7.11

- Fixed issue with progress bar displaying inaccurate details
- Other minor bug fixes
- Updated output for Recheck subcommand for better readability
- Updated documentation
- Updated Readme
- added quiet mode to cli global options `-q`
- Added unit test to fix coverage gaps
- Fixed warnings created by pylint

---

## Version 0.7.10

- Added rebuild module and subcommand see docs for more info
- Added documentation entry for rebuild subcommand
- improved logging messages
- added unit tests
- improved and expanded on type hints
- minor bug fixes

---

## Version 0.7.9

- complete rewrite of the recheck procedures
- Recheck now provides more accuracy and more details
- improvements to the new custom progressbar
- changed the cli argument for the progress bar
- the options are now just 0 and 1
- included new unit tests for all new features
- marked unused functions as deprecated
- added a new hasher object for v2 and hybrid torrents
- minor bug fixes and styling changes

---

## Version 0.7.8

- more updates to logging
- major improvements to progress bar
- removed tqdm as dependency
- implemented custom progress bar logic
- new cli argument controlling the progress bar
- support for pyben 0.3.1
- added threading to recheck module
- added mixins module
- unit test updates and improvements

---

## Version 0.7.5

- updates to logging facility
- fixed bug in created hybrid torrent files
- fixed cli when subcomman not chosen
- doc updates
- unit test updates and improvements

---

## Version 0.7.2

- cleaned up readme and help messages
- removed useless print statements
- improved CI tooling and checking
- minor bug fixes

---

## Version 0.7.1

- split CI integration into separate platform specific files
- added new cli argument `--cwd` which changes the default save
  to location to the current working directory (this will be default in future)
- added unit tests to cover the new argument
- Changed license to a the more permissive Apache 2 software license

---

## Version 0.7.0

- Fixed issues with logging to file.
- Finished adding tests for Unicode Support
- Deprecated some unneccessary code
- Clean up documentation and README
- removed config files no longer in use.

---

## Version 0.6.13

- Fixed bug that created a torrent file with no name.
- Fixed bug that would error if cli path was listed after announce urls
- Added full unicode support.
- Added Unittests for new features and bug fixes

---

## Version 0.6.11

- Fixed bug that occured during recheck when file of 0 length is included.
- Altered Recheck algorithm to process 0 length files.
- Only effected meta version 2 and hybrid torrent files.
- Added unittests to cover the situation.

---

## Version 0.6.10

- Updates to documentation
- Integrated Type hints in source code
- Updated build and CI process

---

## Version 0.6.9

- The --progress flag is now --noprogress
- Default behavior is to show progress bar
- use --noprogress to not show
- added CLI Help format strings
- added custom CLI help formatter class
- Titled Help Message section headers
- Fixed a bunch of error pages created by mkdocs

---

## Version 0.6.8

- Documentation for newest features
- CLI usage examples
- Improved unittests
- made progress bar active by default

---

## Version 0.6.7

- Updates to API

---

## Version 0.6.6

- bug that created faulty Bittorrent V2 meta files in some instances.
- back to working as it should.

---

## Version 0.6.5

- Support for creating Magnet URI's
- Added optional progress bar for torrent creation
- Log File handler
- CLI args page in documentation
- verbose and logging bugs
- multi tracker errors bug

---

## Version 0.6.4

- CLI interface add subcommands
- added interactive mode
- Re-wrote the recheck module
- fixed documentation and docstrings
- linting and testing errors

---

## Version 0.6.3

- Fixed Bug that would format list of trackers incorrectly
- CLI Bug Fixes

---

## Version 0.6.2

- Bug fixes
- Documentation error pages

---

## Version 0.6.0

- cli commands alterations
- debug logging during creation process

---

## Version 0.5.2

- Fixed Bug that was adding wrong fields to info dict

---

## Version 0.5.0

- Slew of new unit tests
- Stricter linting features
- Alternative method of -re-check feature
- Bug Fixes
- CLI help formatting errors

---

## Version 0.4.8

- Improved Algorithm performance for ReCheck.
- Additions to documentation.

---

## Version 0.4.7

- Fixed A bug that misspelled a field when creating Hybrid torrent files.
- Re-Check procedure for v2 and hybrid torrent file checking.

---

## Version 0.4.6

- CLI Help and Usage Messages.
- Expanded CLI args.
- Completely new CheckerClass which replaces old Checker
- Hooks for GUI or other 3rd party apps to hook into Checking
- Documentation and Unit tests for new CheckerClass

---

## Version 0.4.5

- Documentation and docstrings improvements
- Better code formating and more detailed docstrings
- More unit tests.

---

## Version 0.4.2

- The ReChecker feature now supports v1, v2, & hybrid .torrent file.
- Bug in CLI for python &lt; 3.8

---

## Version 0.4.1

- Added tests for hybrid class
- Added logging features
- new cli flag to activate debug mode
- Documentation theme.
- Fixed Bug that allowed improper piece length values.

---

## Version 0.4.0

- Fixed bugs in creating hybrid files.
- Bug Fix that broke cli.

---

## Version 0.3.0

- Added/Improved support for hybrid meta files.
- Many additions to testing suit including linting and coverage tests.

---

## Version 0.2.8

- Styling fixes.
- Bug Fixes.
- Prelimenary support for bittorrent hybrid meta files.
- Bug Fixes

---

## Version 0.2.7

- major imporvements to torrentfile-GUI.
- minor adjustments to this package for integration.
- Code consolidation
- Bug Fixes
- Documentation additions
- Implemented CI/CD Integration

---

## Version 0.2.3

- Bug Fixes
- Code Style and Formatting
- Added more unittests

---

## Version 0.2.1

- Bittorrent Protocol V2 Support
- v2 metafile options to cli
- v2 metafile tests

---

## Version 0.1.7

- Docstrings Improvements.
- Added documentation rederer.
- Improved readme file.
- formatting

---

## Version 0.1.2

- Added a Command Line Interface
- Rough Graphical User Interface
- Minor Bug Fixes
- Improved unittest coverage

---

## Version 0.1.0

- added SHA256 support
- Feeder class for seemless file switching
- Fixed the primary entrypoint function.
- Improved docstrings
- Bug fixes

---

## Version 0.0.2

- Added Unittests
- added bencode support
- added hashing support

---

## Version 0.0.1

- Initial concept and planning
