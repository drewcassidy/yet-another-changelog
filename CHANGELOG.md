# Changelog

All notable changes to this project will be documented in this file

## Unreleased

### Changed

- Cleaned up github actions and index pages in documentation


## Version 1.5.0 - 2024-10-16

### Changed

- Relicensed code under Apache-2.0 license


## Version 1.4.4 - 2024-09-09

### Fixed

- Fixed incorrect version inference in github actions


## Version 1.4.3 - 2024-08-28

### Fixed

- Fixed package missing the cli module in some circumstances

### Changed

- Added the `body-file` output to the github action. `body_file` still exists but is aliased to `body-file`


## Version 1.4.2 - 2024-08-27

### Fixed

- Fixed package failing to install without git history

### Added

- Added the ability to specify the changelog path in the action


## Version 1.4.1 - 2024-08-25

### Fixed

- Fixed escape characters being included in github actions body file

### Added

- Added pypi tags for python 3.11 and 3.12


## Version 1.4.0 - 2024-08-25

### Added

- Added a github action to the repository. The action can create new releases and fetch version information. For more information see the "Github Actions" page in the handbook


## Version 1.3.0 - 2024-08-08

### Added

- Added a `--version` option to `yaclog show` that prints just the version number

### Changed

- Removed support for Click 7 as a dependency


## Version 1.2.0 - 2024-04-16

### Added

- Added the `-s` option to `yaclog release` to increment arbitrary version segments 
- Added the `-n` option to `yaclog release` to create a new release instead of releasing a new one
- Added the `-y` option to `yaclog release` to answer "yes" to all confirmation dialogs. Use with caution!


## Version 1.1.2 - 2022-12-29

### Changed

- Yaclog now only tries to use git when invoked with a command that needs it, meaning most sub commands can now be used on systems without git


## Version 1.1.1 - 2022-08-15

### Fixed

- Fixed `yaclog release -C -c` not committing changes to cargo.toml


## Version 1.1.0 - 2022-08-14

### Added

- Added a flag to update Rust Cargo.toml files when releasing a new version


## Version 1.0.4 - 2022-04-08

### Fixed

- Fixed tests folder being installed as a package


## Version 1.0.3 - 2021-05-12

### Fixed

- Fixed `show` command not working with Click version 8
- Fixed release message incorrectly stating if a commit will be created or not


## Version 1.0.2 - 2021-05-12

### Changed

- Updated to support Click version 8
- Modified module documentation page titles to include a module role

### Fixed

- Fixed tag names with spaces in versions


## Version 1.0.1 - 2021-05-10

### Fixed

- Fixed broken header in new changelogs
- Improved consistency in command documentation metavars


## Version 1.0.0 - 2021-05-07

### Changed

- API changes:
  - `header` attribute renamed to `preamble` to avoid confusion.
- improved version header parsing to be more robust and handle multi-word version names.
- improved version number incrementing in `release`.
  - can now handle other text surrounding a pep440-compliant version number, which will not be modified
  - can now handle pre-releases correctly. The version to increment is the most recent version in the log with a valid pep440 version number in it. 
  - Release increment and prerelease increments can be mixed, allowing e.g: `yaclog release -mr` to create a release candidate with in incremented minor version number.
- `release` base version is now an argument instead of an option, for consistency with other commands.

### Removed

- `entry` with multiple `-b` options no longer add sub bullet points, instead adding each bullet as its own line.

### Added

- Terminal output has color to distinguish version names/headers, sections, and git information.
- Extra newlines are added between versions to improve readability of the raw markdown file.


## Version 0.3.3 - 2021-04-27

### Added

- Unit tests in the `tests` folder

### Fixed

- Default links and dates in VersionEntry are now consistently `None`
- Changelog links dict now contains version links. Modified version links will overwrite those in the table when writing to a file
- Changelog object no longer errors when creating without a path.
- `release` now resets lesser version values when incrementing
- `release` now works with logs that have only unreleased changes


## Version 0.3.2 - 2021-04-24

### Added

- Readme file now has installation and usage instructions.
- yaclog command entry point added to setup.cfg.

### Changed

- `release -c` will no longer create empty commits, and will use the current commit instead.

### Fixed

- `release` and `entry` commands now work using empty changelogs.


## Version 0.3.1 - 2021-04-24

### Added

- `yaclog` tool for manipulating changelogs from the command line
  - `init` command to make a new changelog
  - `format` command to reformat the changelog
  - `show` command to show changes from the changelog
  - `entry` command for manipulating entries in the changelog
  - `tag` command for manipulating tags in the changelog
  - `release` command for creating releases


## Version 0.2.0 - 2021-04-19

### Added

- New yak log logo drawn by my sister

### Changed

- Updated package metadata
- Rewrote parser to use a 2-step method that is more flexible.
  - Parser can now handle code blocks.
  - Parser can now handle setext-style headers and H2s not conforming to the schema.


## Version 0.1.0 - 2021-04-16

First release

### Added

- `yaclog.read()` method to parse changelog files