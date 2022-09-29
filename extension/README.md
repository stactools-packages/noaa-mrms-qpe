# NOAA MRMS QPE Extension Specification

- **Title:** NOAA MRMS QPE
- **Identifier:** <https://raw.githubusercontent.com/stactools-packages/noaa-mrms-qpe/main/extension/schema.json>
- **Field Name Prefix:** noaa_mrms_qpe
- **Scope:** Item, Collection
- **Extension [Maturity Classification](https://github.com/radiantearth/stac-spec/tree/master/extensions/README.md#extension-maturity):** Proposal
- **Owner**: @m-mohr

This document explains the NOAA MRMS QPE Extension to the [SpatioTemporal Asset Catalog](https://github.com/radiantearth/stac-spec) (STAC) specification.

- Examples:
  - [Item example](../examples/item-conus.json): Shows the basic usage of the extension in a STAC Item
  - [Collection example](../examples/collection.json): Shows the basic usage of the extension in a STAC Collection
- [JSON Schema](schema.json)

## Item Properties and derived fields in Collections

| Field Name           | Type    | Description |
| -------------------- | ------- | ----------- |
| noaa_mrms_qpe:pass   | integer | **REQUIRED**. The pass number: `1` = less latency, but less gauges; `2` = more latency, but more gauges. |
| noaa_mrms_qpe:period | integer | **REQUIRED**. The number of hours of the accumulations. One of: `1`, `3`, `6`, `12`, `24`, `48`, `72` |
| noaa_mrms_qpe:region | string  | **REQUIRED**. The region of the data. One of: `CONUS` (Continental US), `HAWAII`, `GUAM`, `ALASKA`, `CARIB` (Caribbean Islands) |

## Contributing

All contributions are subject to the
[STAC Specification Code of Conduct](https://github.com/radiantearth/stac-spec/blob/master/CODE_OF_CONDUCT.md).
For contributions, please follow the
[STAC specification contributing guide](https://github.com/radiantearth/stac-spec/blob/master/CONTRIBUTING.md) Instructions
for running tests are copied here for convenience.
