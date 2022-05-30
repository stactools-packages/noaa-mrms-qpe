from pystac import Link, RelType

REPOSITORY = "https://github.com/stactools-packages/noaa-mrms-qpe"

EXTENSION = (
    "https://raw.githubusercontent.com/stactools-packages/noaa-mrms-qpe"
    "/main/extension/schema.json"
)

EXT_PASS = "noaa_mrms_qpe:pass"
EXT_PERIOD = "noaa_mrms_qpe:period"

EXTENTS = {
    "union": [-176.0, 9.0, 150.0, 72.0],  # Union of all extents
    "conus": [-130.0, 20.0, -60.0, 55.0],  # Continental US
    "hawaii": [-164.0, 15.0, -151.0, 26.0],  # Hawaii
    "guam": [140.0, 9.0, 150.0, 18.0],  # Guam
    "alaska": [-176.0, 50.0, -126.0, 72.0],  # Alaska
    "carib": [-90.0, 10.0, -60.0, 25.0],  # Caribbean
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
