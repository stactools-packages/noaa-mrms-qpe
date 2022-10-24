# stactools-noaa-mrms-qpe

[![PyPI](https://img.shields.io/pypi/v/stactools-noaa-mrms-qpe)](https://pypi.org/project/stactools-noaa-mrms-qpe/)

- Name: noaa-mrms-qpe
- Package: `stactools.noaa_mrms_qpe`
- PyPI: <https://pypi.org/project/stactools-noaa-mrms-qpe/>
- Owner: @m-mohr
- Dataset homepage: <https://mrms.nssl.noaa.gov>
- STAC extensions used:
  - [classification](https://github.com/stac-extensions/classification/)
  - [NOAA MRMS QPE](https://github.com/stac-extensions/noaa-mrms-qpe)
  - [raster](https://github.com/stac-extensions/raster/)
  - [proj](https://github.com/stac-extensions/projection/)
- Extra fields:
  - See the [NOAA MRMS QPE extension](https://github.com/stac-extensions/noaa-mrms-qpe) for details

A stactools package for NOAA's Multi-Radar Multi-Sensor (MRMS) Quantitative Precipitation Estimation (QPE) dataset.

This package can generate STAC files from (gzipped) GRIB2 files that link to the original GRIB2 files and/or
to Cloud-Optimized GeoTiffs (COGs) in the original or any other EPSG projection.

## STAC Examples

- [Collection](examples/collection.json)
- [Item for continental US](examples/item-conus.json)
- [Item for GUAM](examples/item-guam.json)
- [Browse the example in a human-readable form](https://radiantearth.github.io/stac-browser/#/external/raw.githubusercontent.com/stactools-packages/noaa-mrms-qpe/main/examples/collection.json)

## Installation
```shell
pip install stactools-noaa-mrms-qpe
```

## Command-line Usage

### Collection

Create a collection, e.g. 24-hour Pass 2:

```shell
stac noaa-mrms-qpe create-collection collection.json --period 24 --pass_no 2
```

Get information about all options for collection creation:

```shell
stac noaa-mrms-qpe create-collection --help
```

### Item

Create an item for continentel US with a GRIB2 and COG asset:

```shell
stac noaa-mrms-qpe create-item MRMS_MultiSensor_QPE_24H_Pass2_00.00_20220530-120000.grib2.gz item_grib.json --collection collection.json
```

Create an item for ALASKA with only a COG asset converted to EPSG:3857:

```shell
stac noaa-mrms-qpe create-item MRMS_MultiSensor_QPE_24H_Pass2_00.00_20220530-120000.grib2.gz item.json --aoi ALASKA --collection collection.json --nogrib TRUE --epsg 3857
```

Get information about all options for item creation:

```shell
stac noaa-mrms-qpe create-item --help
```

Use `stac noaa-mrms-qpe --help` to see all subcommands and options.

*Note: This package can only read files that contain the timestamp in the file name. It can NOT read the files that contain `latest` instead of a timestamp in the file name.*

## Contributing

We use [pre-commit](https://pre-commit.com/) to check any changes.
To set up your development environment:

```shell
$ pip install -e .
$ pip install -r requirements-dev.txt
$ pre-commit install
```

To check all files:

```shell
$ pre-commit run --all-files
```

To run the tests:

```shell
$ pytest -vv
```
