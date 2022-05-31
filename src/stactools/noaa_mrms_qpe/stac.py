import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Union

import rasterio
from pystac import (
    Asset,
    CatalogType,
    Collection,
    Extent,
    Item,
    MediaType,
    Provider,
    ProviderRole,
    SpatialExtent,
    Summaries,
    TemporalExtent,
)
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.raster import DataType, RasterBand, RasterExtension
from pystac.extensions.timestamps import TimestampsExtension

from . import cog, constants

logger = logging.getLogger(__name__)


def create_collection(period: int, pass_no: int, thumbnail: str = "") -> Collection:
    """Create a STAC Collection for NOAA MRMS QPE sub-products.

    Args:
        period (int): The time period the sub-product is for (either 1, 3, 6, 12, 24, 48, or 72)
        pass_no (int): The pass number of the sub-product (either 1 or 2)
        thumbnail (str): URL for the collection thumbnail asset (none if empty)

    Returns:
        Collection: STAC Collection object
    """
    providers = [
        Provider(
            name="NOAA National Severe Storms Laboratory",
            roles=[ProviderRole.PRODUCER, ProviderRole.LICENSOR],
            url="https://www.nssl.noaa.gov/projects/mrms",
        ),
        Provider(
            name="Stactools",
            roles=[ProviderRole.PROCESSOR],
            description="Conversion from GRIB to COG files",
            url=constants.REPOSITORY,
        ),
    ]

    # Time must be in UTC
    demo_time = datetime.now(tz=timezone.utc)

    spatial_extents = list(constants.EXTENTS.values())
    extent = Extent(
        SpatialExtent(spatial_extents),
        TemporalExtent([[demo_time, None]]),
    )

    keywords = [
        "NOAA",
        "MRMS",
        "QPE",
        "multi-radar",
        "multi-sensor",
        "precipitation",
        "{t}-hour".format(t=period),
    ]

    description = (
        "The Multi-Radar Multi-Sensor (MRMS) quantitative precipitation estimation "
        "(QPE) product is generated fully automatically from multiple sources to generate "
        "seamless, hourly 1 km mosaics over the US.\n\n"
    )
    if pass_no == 1:
        description += (
            "This is the {t}-hour pass 1 product with less latency (60 min), "
            "but less gauges (60-65 %)."
        )
    elif pass_no == 2:
        description += (
            "This is the {t}-hour pass 2 product with more latency (120 min), "
            "but more gauges (99 %)."
        )

    summaries = Summaries({})
    summaries.add(constants.EXT_PASS, [pass_no])
    summaries.add(constants.EXT_PERIOD, [period])

    collection = Collection(
        stac_extensions=[constants.EXTENSION],
        id="noaa-mrms-qpe-{t}h-pass{p}".format(t=period, p=pass_no),
        title="NOAA MRMS QPE {t}-hour Pass {p}".format(t=period, p=pass_no),
        description=description.format(t=period),
        keywords=keywords,
        license="proprietary",
        providers=providers,
        extent=extent,
        summaries=summaries,
        catalog_type=CatalogType.RELATIVE_PUBLISHED,
    )

    collection.add_link(constants.LINK_LICENSE)
    collection.add_link(constants.LINK_MRMS_HOME)
    collection.add_link(constants.LINK_MRMS_TECH_GUIDE)

    if len(thumbnail) > 0:
        if thumbnail.endswith(".png"):
            media_type = MediaType.PNG
        else:
            media_type = MediaType.JPEG

        collection.add_asset(
            "thumbnail",
            Asset(
                href=thumbnail,
                title="Preview",
                roles=["thumbnail"],
                media_type=media_type,
            ),
        )

    return collection


def create_item(
    asset_href: str,
    aoi: str = "CONUS",
    collection: Union[Collection, None] = None,
    to_cog: bool = False,
    epsg: int = 0,
) -> Item:
    """Create a STAC Item

    This function should include logic to extract all relevant metadata from an
    asset, metadata asset, and/or a constants.py file.

    See `Item<https://pystac.readthedocs.io/en/latest/api.html#item>`_.

    Args:
        asset_href (str): The HREF pointing to an asset associated with the item
        aoi (str): The area of interest, either 'ALASKA', 'CONUS' (continental US, default),
            'CARIB' (Caribbean islands), 'GUAM' or 'HAWAII'
        collection (pystac.Collection): HREF to an existing collection
        to_cog (bool): Converts the GRIB2 files to COG if set to true.
            Defaults to false, which keeps the file as is.

    Returns:
        Item: STAC Item object
    """

    basics = parse_filename(asset_href)
    id = aoi + "_" + basics["id"]

    bbox = constants.EXTENTS[aoi]

    description = "Multi-sensor accumulation {p}-hour ({t}-hour latency) [mm]".format(
        p=basics["period"], t=basics["pass_no"]
    )

    properties = {
        constants.EXT_PASS: basics["pass_no"],
        constants.EXT_PERIOD: basics["period"],
        "description": description,
        "gsd": constants.RESOLUTION_M,
    }

    item = Item(
        stac_extensions=[constants.EXTENSION],
        id=id,
        properties=properties,
        geometry=bbox_to_polygon(bbox),
        bbox=bbox,
        datetime=basics["datetime"],
        collection=collection,
    )

    extra_fields: Dict[str, Any] = {}
    crs = None
    media_type = ""
    href = ""

    if to_cog:
        if epsg > 0:
            crs = "epsg:" + str(epsg)
        media_type = MediaType.COG
        href = cog.convert(asset_href, unzip=basics["gzip"], reproject_to=crs)
    else:
        media_type = "application/wmo-GRIB2"
        if basics["gzip"]:
            href = cog.decompress(asset_href)
        else:
            href = asset_href

        # we have to use file extension v1.0.0 as no other extension
        # supports to specify multiple no-data values.
        # The GRIB files from NOAA have two no-data values though (-1, -3).
        item.stac_extensions.append(
            "https://stac-extensions.github.io/file/v1.0.0/schema.json"
        )
        extra_fields["file:data_type"] = constants.GRIB_DATATYPE
        extra_fields["file:nodata"] = constants.GRIB_NODATA
        extra_fields["file:unit"] = constants.UNIT

    # Add an asset to the item (COG for example)
    asset = Asset(
        href=href, media_type=media_type, roles=["data"], extra_fields=extra_fields
    )
    item.add_asset("data", asset)

    ts_attrs = TimestampsExtension.ext(asset, add_if_missing=True)
    ts_attrs.expires = basics["datetime"]

    shape = None
    if to_cog:
        raster_attrs = RasterExtension.ext(asset, add_if_missing=True)

        bands = []
        with rasterio.open(href) as dataset:
            if len(dataset.shape) == 2:
                shape = [dataset.shape[1], dataset.shape[0]]
            for (i, _) in enumerate(dataset.indexes):
                band = RasterBand.create()
                band.spatial_resolution = constants.RESOLUTION_M
                band.unit = constants.UNIT
                band.nodata = dataset.nodatavals[i]
                band.data_type = DataType(dataset.dtypes[i])
                bands.append(band)

        raster_attrs.bands = bands
    else:
        shape = constants.SHAPES[aoi]

    proj_attrs = ProjectionExtension.ext(item, add_if_missing=True)
    if shape:
        proj_attrs.shape = shape

    if to_cog and epsg > 0:
        proj_attrs.epsg = epsg
    else:
        proj_attrs.epsg = None
        proj_attrs.projjson = constants.PROJJSON

    return item


def parse_filename(path: str) -> Dict[str, Any]:
    filename = os.path.basename(path)
    parts = constants.FILENAME_PATTERN.match(filename)
    if parts is None:
        raise ValueError("Filename is not valid")

    year = int(parts.group(4))
    month = int(parts.group(5))
    day = int(parts.group(6))
    hour = int(parts.group(7))
    time = datetime(year, month, day, hour, tzinfo=timezone.utc)

    return {
        "id": parts.group(1),
        "period": int(parts.group(2)),
        "pass_no": int(parts.group(3)),
        "datetime": time,
        "gzip": False if parts.group(8) is None else True,
    }


def bbox_to_polygon(b: List[float]) -> Dict[str, Any]:
    return {
        "type": "Polygon",
        "coordinates": [
            [[b[0], b[3]], [b[2], b[3]], [b[2], b[1]], [b[0], b[1]], [b[0], b[3]]]
        ],
    }
