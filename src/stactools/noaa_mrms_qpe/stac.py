import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import rasterio
from fileinfo import FileInfo
from pystac import (
    Asset,
    CatalogType,
    Collection,
    Extent,
    Item,
    MediaType,
    SpatialExtent,
    Summaries,
    TemporalExtent,
)
from pystac.extensions.item_assets import AssetDefinition, ItemAssetsExtension
from pystac.extensions.projection import ProjectionExtension
from pystac.extensions.raster import SCHEMA_URI as RASTER_EXTENSION
from pystac.extensions.raster import DataType, RasterBand, RasterExtension
from pystac.extensions.timestamps import TimestampsExtension

from . import cog, constants

logger = logging.getLogger(__name__)


def create_collection(
    period: int, pass_no: int, thumbnail: str = "", cog: bool = False
) -> Collection:
    """Create a STAC Collection for NOAA MRMS QPE sub-products.

    Args:
        period (int): The time period the sub-product is for (either 1, 3, 6, 12, 24, 48, or 72)
        pass_no (int): The pass number of the sub-product (either 1 or 2)
        thumbnail (str): URL for the collection thumbnail asset (none if empty)
        cog (bool): Set to TRUE if the items contain COG files. Otherwise, GRIB2 files are expected.

    Returns:
        Collection: STAC Collection object
    """
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
        providers=constants.PROVIDERS,
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

    data_asset: Dict[str, Any] = {"roles": constants.ASSET_ROLES, "type": ""}

    # it seems the raster extension can't be added to an AssetDefintion
    # RasterExtension.ext(data_asset, add_if_missing=True)
    # RasterBand.create()
    # etc. are not usable here
    collection.stac_extensions.append(RASTER_EXTENSION)
    band: Dict[str, Any] = {}
    band["spatial_resolution"] = constants.RESOLUTION_M
    band["unit"] = constants.UNIT

    if cog:
        data_asset["type"] = MediaType.COG

        band["nodata"] = constants.COG_NODATA
    else:
        data_asset["type"] = constants.GRIB_MEDIATYPE

        # we have to use file extension v1.0.0 as no other extension
        # supports to specify multiple no-data values.
        # The GRIB files from NOAA have two no-data values though (-1, -3).
        collection.stac_extensions.append(constants.FILE_EXTENSION_V1)
        data_asset["file:data_type"] = constants.GRIB_DATATYPE
        data_asset["file:nodata"] = constants.GRIB_NODATA
        data_asset["file:unit"] = constants.UNIT

    data_asset["raster:bands"] = [band]

    item_assets_attrs = ItemAssetsExtension.ext(collection, add_if_missing=True)
    item_assets_attrs.item_assets = {constants.ASSET_KEY: AssetDefinition(data_asset)}

    return collection


def create_item(
    asset_href: str,
    aoi: str = "CONUS",
    collection: Optional[Collection] = None,
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
    id = aoi + "_" + basics.id

    bbox = constants.EXTENTS[aoi]

    description = "Multi-sensor accumulation {p}-hour ({t}-hour latency) [mm]".format(
        p=basics.period, t=basics.pass_no
    )

    properties = {
        constants.EXT_PASS: basics.pass_no,
        constants.EXT_PERIOD: basics.period,
        "description": description,
    }

    item = Item(
        stac_extensions=[constants.EXTENSION],
        id=id,
        properties=properties,
        geometry=bbox_to_polygon(bbox),
        bbox=bbox,
        datetime=basics.datetime,
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
        href = cog.convert(asset_href, unzip=basics.gzip, reproject_to=crs)
    else:
        media_type = constants.GRIB_MEDIATYPE
        if basics.gzip:
            href = cog.decompress(asset_href)
        else:
            href = asset_href

    if not to_cog:
        # we have to use file extension v1.0.0 as no other extension
        # supports to specify multiple no-data values.
        # The GRIB files from NOAA have two no-data values though (-1, -3).
        item.stac_extensions.append(constants.FILE_EXTENSION_V1)
        extra_fields["file:data_type"] = constants.GRIB_DATATYPE
        extra_fields["file:nodata"] = constants.GRIB_NODATA
        extra_fields["file:unit"] = constants.UNIT

    # Add an asset to the item (COG for example)
    asset = Asset(
        href=href,
        media_type=media_type,
        roles=constants.ASSET_ROLES,
        extra_fields=extra_fields,
    )
    item.add_asset(constants.ASSET_KEY, asset)

    ts_attrs = TimestampsExtension.ext(asset, add_if_missing=True)
    ts_attrs.expires = basics.datetime

    shape = None
    transform = None
    with rasterio.open(href) as dataset:
        if dataset.transform:
            transform = list(dataset.transform)[0:6]

        if len(dataset.shape) == 2:
            shape = [dataset.shape[1], dataset.shape[0]]

        if len(dataset.indexes) == 1:
            band = RasterBand.create()
            band.spatial_resolution = constants.RESOLUTION_M
            band.unit = constants.UNIT
            band.data_type = DataType(dataset.dtypes[0])
            if to_cog:
                band.nodata = constants.COG_NODATA

            raster_attrs = RasterExtension.ext(asset, add_if_missing=True)
            raster_attrs.bands = [band]

    proj_attrs = ProjectionExtension.ext(item, add_if_missing=True)
    if shape:
        proj_attrs.shape = shape

    if transform:
        proj_attrs.transform = transform

    if to_cog and epsg > 0:
        proj_attrs.epsg = epsg
    else:
        proj_attrs.epsg = None
        proj_attrs.projjson = constants.PROJJSON

    return item


def parse_filename(path: str) -> FileInfo:
    filename = os.path.basename(path)
    parts = constants.FILENAME_PATTERN.match(filename)
    if parts is None:
        raise ValueError("Filename is not valid")

    year = int(parts.group(4))
    month = int(parts.group(5))
    day = int(parts.group(6))
    hour = int(parts.group(7))
    time = datetime(year, month, day, hour, tzinfo=timezone.utc)

    return FileInfo(
        id=parts.group(1),
        period=int(parts.group(2)),
        pass_no=int(parts.group(3)),
        datetime=time,
        gzip=False if parts.group(8) is None else True,
    )


def bbox_to_polygon(b: List[float]) -> Dict[str, Any]:
    return {
        "type": "Polygon",
        "coordinates": [
            [[b[0], b[3]], [b[2], b[3]], [b[2], b[1]], [b[0], b[1]], [b[0], b[3]]]
        ],
    }
