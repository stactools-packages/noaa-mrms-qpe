import enum
import re
from typing import Any, Dict

from pystac import Link, Provider, ProviderRole, RelType


class AOI(str, enum.Enum):
    CONUS = "CONUS"
    HAWAII = "HAWAII"
    GUAM = "GUAM"
    ALASKA = "ALASKA"
    CARIB = "CARIB"


EXTENSION = (
    "https://raw.githubusercontent.com/stactools-packages/noaa-mrms-qpe"
    "/main/extension/schema.json"
)
RASTER_EXTENSION_V11 = "https://stac-extensions.github.io/raster/v1.1.0/schema.json"
CLASSIFICATION_EXTENSION_V11 = (
    "https://stac-extensions.github.io/classification/v1.1.0/schema.json"
)

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

PROVIDERS = [
    Provider(
        name="NOAA National Severe Storms Laboratory",
        roles=[ProviderRole.PRODUCER, ProviderRole.LICENSOR],
        url="https://www.nssl.noaa.gov/projects/mrms",
    ),
]

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

PROJJSON: Dict[str, Any] = {
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
# The files report a slightly smaller resolution, but 1000m / 1km is defined
# in the official documentation so I'm following the official docs for now
RESOLUTION_M = 1000

ASSET_GRIB2_KEY = "grib2"
ASSET_GRIB2_TITLE = "Original GRIB2 file"
GRIB2_NODATA = [-1, -3]
GRIB2_MEDIATYPE = "application/wmo-GRIB2"
GRIB2_ROLES = ["data", "source"]
GRIB2_CLASSIFICATION = [
    {
        "value": -1,
        "name": "missing-value",
        "description": "Missing value (no-data)",
        # the nodata flag is not supported yet in classification ext v1.1,
        # but is also doesn't hurt to add it already.
        # the same applies for all other occurrences below
        # https://github.com/stac-extensions/classification/pull/32
        "nodata": True,
    },
    {
        "value": -3,
        "name": "no-coverage",
        "description": "No coverage (no-data)",
        "nodata": True,
    },
    {
        "value": -999,
        "name": "no-coverage",
        "description": "No coverage (no-data)",
        "nodata": True,
    },
]

ASSET_COG_KEY = "cog"
ASSET_COG_TITLE = "Processed Cloud-optimized GeoTiff file"
COG_COMPRESS = "LZW"
COG_NODATA = -1
COG_ROLES = ["data", "cloud-optimized"]
COG_CLASSIFICATION = {
    "value": -1,
    "name": "no-data",
    "description": "No coverage or missing value (no-data)",
    "nodata": True,
}
