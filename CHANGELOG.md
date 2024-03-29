# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [0.3.1]

### Fixed

- Capture the minutes and seconds from the file names as they are not always 0

## [0.3.0]

### Added

- New property `noaa_mrms_qpe:region`

### Changed

- Moved extension to separate repository: <https://github.com/stac-extensions/noaa-mrms-qpe>
- Always add `proj:epsg` to Item to fulfill a proj extension "requirement" (schema issue in 1.0.0).

### Fixed

- Changed casing of Cloud-Optimized in the asset titles

## [0.2.0]

### Added

- New property `noaa_mrms_qpe:region` added to Items and Collections
- Officially add support for Python 3.10

### Fixed

- remove unused portions of CI that are causing problems

## [0.1.1]

### Changed

- cast numpy float64s to float

### Fixed

- remove unused portions of CI that are causing problems

## [0.1.0]

- First release

[Unreleased]: <https://github.com/stactools-packages/noaa-mrms-qpe/tree/main/>
[0.3.1]: <https://github.com/stactools-packages/noaa-mrms-qpe/tree/v0.3.1/>
[0.3.0]: <https://github.com/stactools-packages/noaa-mrms-qpe/tree/v0.3.0/>
[0.2.0]: <https://github.com/stactools-packages/noaa-mrms-qpe/tree/v0.2.0/>
[0.1.1]: <https://github.com/stactools-packages/noaa-mrms-qpe/tree/v0.1.1/>
[0.1.0]: <https://github.com/stactools-packages/noaa-mrms-qpe/tree/v0.1.0/>
