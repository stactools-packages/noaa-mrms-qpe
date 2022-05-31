import re

from pystac import Link, RelType

REPOSITORY = "https://github.com/stactools-packages/noaa-mrms-qpe"

EXTENSION = (
    "https://raw.githubusercontent.com/stactools-packages/noaa-mrms-qpe"
    "/main/extension/schema.json"
)
FILE_EXTENSION_V1 = "https://stac-extensions.github.io/file/v1.0.0/schema.json"

EXT_PASS = "noaa_mrms_qpe:pass"
EXT_PERIOD = "noaa_mrms_qpe:period"

EXTENTS = {
    "UNION": [-176.0, 9.0, 150.0, 72.0],  # Union of all extents
    "CONUS": [-130.0, 20.0, -60.0, 55.0],  # Continental US
    "HAWAII": [-164.0, 15.0, -151.0, 26.0],  # Hawaii
    "GUAM": [140.0, 9.0, 150.0, 18.0],  # Guam
    "ALASKA": [-176.0, 50.0, -126.0, 72.0],  # Alaska
    "CARIB": [-90.0, 10.0, -60.0, 25.0],  # Caribbean
}

SHAPES = {
    "CONUS": [7000, 3500],
    "HAWAII": [2600, 2200],
    "GUAM": [2000, 1800],
    "ALASKA": [5000, 2200],
    "CARIB": [3000, 1500],
}

LINK_LICENSE = Link(
    target="https://www.nssl.noaa.gov/projects/mrms/nmq_data_policy_OGCrevised.pdf",
    rel=RelType.LICENSE,
    media_type="application/pdf",
    title="MRMS Dataset Sharing Policy",
)
LINK_MRMS_HOME = Link(
    target="https://mrms.nssl.noaa.gov",
    rel="about",
    media_type="text/html",
    title="MRMS Homepage",
)
LINK_MRMS_TECH_GUIDE = Link(
    target="https://vlab.noaa.gov/web/wdtd/-/multi-sensor-qpe-1?selectedFolder=9234881",
    rel="about",
    media_type="text/html",
    title="MRMS QPE Technical Product Guide",
)

FILENAME_PATTERN = re.compile(
    r"^(MRMS_MultiSensor_QPE_(\d{2})H_Pass(\d)_\d+\.\d+_(\d{4})(\d{2})(\d{2})-(\d{2})0000)\.grib2(\.gz)?$"  # noqa: E501
)

PROJJSON = {
    "$schema": "https://proj.org/schemas/v0.4/projjson.schema.json",
    "type": "GeographicCRS",
    "name": "unknown",
    "datum": {
        "type": "GeodeticReferenceFrame",
        "name": "unknown",
        "ellipsoid": {
            "name": "unknown",
            "semi_major_axis": 6378160,
            "inverse_flattening": 298.253916296469,
        },
    },
    "coordinate_system": {
        "subtype": "ellipsoidal",
        "axis": [
            {
                "name": "Longitude",
                "abbreviation": "lon",
                "direction": "east",
                "unit": "degree",
            },
            {
                "name": "Latitude",
                "abbreviation": "lat",
                "direction": "north",
                "unit": "degree",
            },
        ],
    },
}

UNIT = "mm"
RESOLUTION_M = 1000  # 1km

GRIB_DATATYPE = "float64"
GRIB_NODATA = [-1, -3]
GRIB_MEDIATYPE = "application/wmo-GRIB2"

ASSET_KEY = "data"
ASSET_ROLES = ["data"]
