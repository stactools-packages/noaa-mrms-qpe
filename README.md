# stactools-noaa-mrms-qpe

[![PyPI](https://img.shields.io/pypi/v/stactools-noaa-mrms-qpe)](https://pypi.org/project/stactools-noaa-mrms-qpe/)

- Name: noaa-mrms-qpe
- Package: `stactools.noaa_mrms_qpe`
- PyPI: <https://pypi.org/project/stactools-noaa-mrms-qpe/>
- Owner: @m-mohr
- Dataset homepage: <https://mrms.nssl.noaa.gov>
- STAC extensions used:
  - [classification v1.1.0](https://github.com/stac-extensions/classification/) (for COG masks)
  - [file v1.0.0](https://github.com/stac-extensions/file/) (for GRIB export)
  - [raster v1.1.0](https://github.com/stac-extensions/raster/) (for COG export)
  - [proj](https://github.com/stac-extensions/projection/)
- Extra fields:
  - See [NOAA MRMS QPE extension](./extension/README.md) for details

A stactools package for NOAA's Multi-Radar Multi-Sensor (MRMS) Quantitative Precipitation Estimation (QPE) dataset.

This package can generate STAC files from (gzipped) GRIB2 files and that either link to the original GRIB2 files or
to cloud-optimized GeoTiffs (COGs) in the original or any other EPSG projection.

## STAC Examples

- For COGs assets:
  - [Collection](examples/cog/collection.json)
  - [Item](examples/cog/item.json)
  - [Browse the example in a human-readable form](https://radiantearth.github.io/stac-browser/#/external/raw.githubusercontent.com/stactools-packages/noaa-mrms-qpe/main/examples/cog/collection.json)
- For GRIB2 assets:
  - [Collection](examples/grib/collection.json)
  - [Item](examples/grib/item.json)
  - [Browse the example in a human-readable form](https://radiantearth.github.io/stac-browser/#/external/raw.githubusercontent.com/stactools-packages/noaa-mrms-qpe/main/examples/grib/collection.json)

## Installation
```shell
pip install stactools-noaa-mrms-qpe
```

## Command-line Usage

### Collection

Create a collection, e.g. 24-hour Pass 2:

```shell
stac noaa_mrms_qpe create-collection collection.json --period 24 --pass_no 2
```

Get information about all options for collection creation:

```shell
stac noaa_mrms_qpe create-collection --help
```

### Item

Create an item for continentel US with a GRIB2 asset:

```shell
stac noaa_mrms_qpe create-item MRMS_MultiSensor_QPE_24H_Pass2_00.00_20220530-120000.grib2.gz item_grib.json --collection collection.json
```

Create an item for ALASKA with a COG asset converted to EPSG:3857:

```shell
stac noaa_mrms_qpe create-item MRMS_MultiSensor_QPE_24H_Pass2_00.00_20220530-120000.grib2.gz item.json --aoi ALASKA --collection collection.json --cog TRUE --epsg 3857
```

Get information about all options for item creation:

```shell
stac noaa_mrms_qpe create-item --help
```

Use `stac noaa-mrms-qpe --help` to see all subcommands and options.

Note: This package can only read files that contain the timestamp in the file name. It can NOT read the files that contain `latest` instead of a timestamp in the file name.

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
