# stactools-noaa-mrms-qpe

[![PyPI](https://img.shields.io/pypi/v/stactools-noaa-mrms-qpe)](https://pypi.org/project/stactools-noaa-mrms-qpe/)

- Name: noaa-mrms-qpe
- Package: `stactools.noaa_mrms_qpe`
- PyPI: https://pypi.org/project/stactools-noaa-mrms-qpe/
- Owner: @m-mohr
- Dataset homepage: https://mrms.nssl.noaa.gov
- STAC extensions used:
  - [proj](https://github.com/stac-extensions/projection/)
- Extra fields:
  - `noaa-mrms-qpe:custom`: A custom attribute

A stactools package for NOAA's Multi-Radar Multi-Sensor (MRMS) Quantitative Precipitation Estimation (QPE) dataset.

## STAC Examples

- [Collection](examples/collection.json)
- [Item](examples/item/item.json)

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

Create an item:

```shell
stac noaa_mrms_qpe create-item MRMS_MultiSensor_QPE_24H_Pass2_00.00_20220530-120000.grib2.gz item.json --aoi CONUS --collection collection.json --cog TRUE
```

Get information about all options for item creation:

```shell
stac noaa_mrms_qpe create-item --help
```

Use `stac noaa-mrms-qpe --help` to see all subcommands and options.

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

## Roadmap

- [ ] Implementation
- [ ] Tests
- [ ] Documentation
- [x] Examples
