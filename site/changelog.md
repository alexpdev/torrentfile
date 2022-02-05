# TorrentFile

## Version 0.6.9

### Changed

    - The --progress flag is now --noprogress
    - Default behavior is to show progress bar
    - use --noprogress to not show

### Improved

    - Documentation
    - CLI Help format strings

### Added

    - Custom CLI help formatter class 
    - Titled Help Message section headers

---------------------

## Version 0.6.8

### Added

    - Documentation for newest features
    - CLI usage examples
    - Improved unittests
    - made progress bar active by default

---------------------

## Version 0.6.7

### Fixed

    - Updates to API

---------------------

## Version 0.6.6

### Fixed

    - bug that created faulty Bittorrent V2 meta files in some instances.
    - back to working as it should.

---------------------

## Version 0.6.5

### Added

    - Support for creating Magnet URI's
    - Added optional progress bar for torrent creation
    - Log File handler
    - CLI args page in documentation

### Fixed

    - verbose and logging bugs
    - multi tracker errors bug

---------------------

## Version 0.6.4

### Fixed/Added

    - CLI interface add subcommands
    - added interactive mode
    - Re-wrote the recheck module
    - fixed documentation and docstrings
    - linting and testing errors

---------------------

## Version 0.6.3

### Fixed

    - Bug that would format list of trackers incorrectly
    - CLI Bug Fixes

---------------------

## Version 0.6.2

### Fixed

    - Bug fixes
    - Documentation error pages

---------------------

## Version 0.6.0

## Changed

    - cli commands alterations

## Added

    - debug logging during creation process

---------------------

## Version 0.5.2

### Fixed

    - Major Bug that was adding `announce-list` to info dict

---------------------

## Version 0.5.0

### Added

    - Slew of new unit tests
    - Stricter linting features
    - Alternative method of -re-check feature

### Fixed

    - Bug Fixes
    - CLI help formatting errors

---------------------

## Version 0.4.8

### Improved

    - Algorithm performance for ReCheck.
    - Additions to documentation.

---------------------

## Version 0.4.7

### Fixed

    - A bug that misspelled a field when creating Hybrid torrent files.

### Improved

    - Re-Check procedure for v2 and hybrid torrent file checking.

---------------------

## Version 0.4.6

### Improved

    - CLI Help and Usage Messages.
    - Expanded CLI args.

### Added

    - Completely new CheckerClass which replaces old Checker
    - Hooks for GUI or other 3rd party apps to hook into Checking
    - Documentation and Unit tests for new CheckerClass

---------------------

## Version 0.4.5

### Added

    - Documentation and docstrings.
    - Better formating and more detailed.
    - More unit tests.

---------------------

## Version 0.4.3

### Fixed

    - Bug Fixes

---------------------

## Version 0.4.2

### Added

    - The ReChecker feature now supports v1, v2, & hybrid .torrent file.

### Fixed

    - Bug in CLI for python < 3.8

---------------------

## Version 0.4.1

### Added

    - Added tests for hybrid class
    - logging feature
    - new cli flag to activate debug mode
    - Documentation theme.

### Fixed

    - Bug that allowed improper piece length values.

---------------------

## Version 0.4.0

### Fixed

    - Fixed bugs in creating hybrid files.

---------------------

## Version 0.3.1

### Fixed

    - Bug Fix that broke cli.

---------------------

## Version 0.3.0

### Added

    - Added/Improved support for hybrid meta files.
    - Many additions to testing suit including linting and coverage tests.

### Fixed

    - Styling fixes.
    - Bug Fixes.

---------------------

## Version 0.2.8

### Added

    - Prelimenary support for bittorrent hybrid meta files.
    - CI/CD integration.

### Fixed

    - Bug Fixes

---------------------

## Version 0.2.7

### Added

    - major imporvements to torrentfile-GUI.
    - minor adjustments to this package for integration.

### Fixes

    - Code consolidation
    - Bug Fixes

---------------------

## Version 0.2.6

### Added

    - Documentation

---------------------

## Version 0.2.5

### Added

    - Bug Fixes
    - CI/CD Integration

---------------------

## Version 0.2.3

### Fixed

    - Bug Fixes
    - Code Style and Formatting

---------------------

## Version 0.2.2

### Added

    - improved test suit

---------------------

## Version 0.2.1

### Added

    - Bittorrent Protocol V2 Support
    - v2 metafile options to cli
    - v2 metafile tests

---------------------

## Version 0.1.7

### Added

    - Docstrings Improvements
    - Documentation Improvements

### Fixed

    - readme file update
    - formatting

---------------------

## Version 0.1.6

### Fixed

    - Bug Fixes

---------------------

## Version 0.1.4

### Removed

    - Graphical User Interface.
    - the GUI is now packaged seperately. See README for details.

---------------------

## Version 0.1.3

## Added

    - Rough Bittorrent v2 protocol support
    - BugFixes

---------------------

## Version 0.1.2

## Added

    - Command Line Interface
    - Rough Graphical User Interface

## Fixed

    - Minor Bug Fixes

---------------------

## Version 0.1.1

## Added

    - Test suite

## Fixed

    - Bug Fixes

---------------------

## Version 0.1.0

### Added

    - SHA256 support
    - Feeder class for seemless file switching

### Fixed

    - Primary function now works
    - Better docstrings
    - Bug fixes

---------------------

## Version 0.0.2

### Added

    - Test suite
    - bencoding support
    - hashing support

---------------------

## Version 0.0.1

    - Initial concept and planning
