import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

import numpy as np
import rasterio
from dateutil.parser import isoparse
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
from pystac.extensions.raster import DataType

from . import cog, constants
from .fileinfo import FileInfo

logger = logging.getLogger(__name__)


def create_collection(
    period: int,
    pass_no: int,
    thumbnail: str = "",
    nocog: bool = False,
    nogrib: bool = False,
    start_time: Optional[str] = None,
) -> Collection:
    """Create a STAC Collection for NOAA MRMS QPE sub-products.

    Args:
        period (int): The time period the sub-product is for (either 1, 3, 6, 12, 24, 48, or 72)
        pass_no (int): The pass number of the sub-product (either 1 or 2)
        thumbnail (str): URL for the PNG or JPEG collection thumbnail asset (none if empty)
        nocog (bool): If set to True, the collections does not include the COG-related metadata
        nogrib (bool): If set to True, the collections does not include the GRIB2-related metadata
        start_time (str): The start timestamp for the temporal extent, default to now.
            Timestamps consist of a date and time in UTC and must follow RFC 3339, section 5.6.

    Returns:
        Collection: STAC Collection object
    """
    # Time must be in UTC
    if start_time is None:
        start_datetime = datetime.now(tz=timezone.utc)
    else:
        start_datetime = isoparse(start_time)

    spatial_extents = list(constants.EXTENTS.values())
    extent = Extent(
        SpatialExtent(spatial_extents),
        TemporalExtent([[start_datetime, None]]),
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
    if not nogrib:
        keywords.append("GRIB2")
    if not nocog:
        keywords.append("COG")

    description = (
        "The Multi-Radar Multi-Sensor (MRMS) quantitative precipitation estimation "
        "(QPE) product is generated fully automatically from multiple sources to generate "
        "seamless, hourly 1 km mosaics over the US.\n\n"
        "**Note:** The data for Guam and the Caribbean Islands are [not multi-sensor products]"
        "(https://vlab.noaa.gov/documents/96675/666999/MS_DomainDiffernces.png) yet."
    )
    if pass_no == 1:
        description += (
            "\n\nThis is the {t}-hour pass 1 product with less latency (60 min), "
            "but less gauges (60-65 %)."
        )
    elif pass_no == 2:
        description += (
            "\n\nThis is the {t}-hour pass 2 product with more latency (120 min), "
            "but more gauges (99 %)."
        )

    summaries = Summaries({})
    summaries.add(constants.EXT_PASS, [pass_no])
    summaries.add(constants.EXT_PERIOD, [period])
    summaries.add(constants.EXT_REGION, [e.value for e in constants.AOI])

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

    item_assets = {}

    # it seems the raster extension can't be added to an AssetDefintion
    # via RasterExtension.ext(data_asset, add_if_missing=True).
    # So RasterBand.create() etc. are not usable here
    collection.stac_extensions.append(constants.RASTER_EXTENSION_V11)

    def create_asset(media_type: str, roles: List[str], title: str) -> Dict[str, Any]:
        asset: Dict[str, Any] = {
            "roles": roles,
            "type": media_type,
            "raster:bands": [create_band()],
            "title": title,
        }
        return asset

    if not nocog:
        asset = create_asset(
            MediaType.COG, constants.COG_ROLES, constants.ASSET_COG_TITLE
        )
        item_assets[constants.ASSET_COG_KEY] = AssetDefinition(asset)

    if not nogrib:
        asset = create_asset(
            constants.GRIB2_MEDIATYPE,
            constants.GRIB2_ROLES,
            constants.ASSET_GRIB2_TITLE,
        )
        item_assets[constants.ASSET_GRIB2_KEY] = AssetDefinition(asset)

    item_assets_attrs = ItemAssetsExtension.ext(collection, add_if_missing=True)
    item_assets_attrs.item_assets = item_assets

    return collection


def create_item(
    asset_href: str,
    aoi: constants.AOI,
    collection: Optional[Collection] = None,
    nocog: bool = False,
    nogrib: bool = False,
    epsg: int = 0,
) -> Item:
    """Create a STAC Item

    This function should include logic to extract all relevant metadata from an
    asset, metadata asset, and/or a constants.py file.

    See `Item<https://pystac.readthedocs.io/en/latest/api.html#item>`_.

    Args:
        asset_href (str): The HREF pointing to an asset associated with the item
        aoi (AOI): The area of interest, either 'ALASKA', 'CONUS' (continental US),
            'CARIB' (Caribbean islands), 'GUAM' or 'HAWAII'
        collection (pystac.Collection): HREF to an existing collection
        nocog (bool): If set to True, no COG file is generated for the Item
        nogrib (bool): If set to True, the GRIB2 file is not added to the Item
        epsg (int): Converts the COG files to the given EPSG Code (e.g. 3857),
            doesn't reproject by default.

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
        constants.EXT_REGION: aoi.value,
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

    # Raster extension v1.1 not supported by PySTAC
    item.stac_extensions.append(constants.RASTER_EXTENSION_V11)
    # Classification extension v1.1 not supported by PySTAC
    item.stac_extensions.append(constants.CLASSIFICATION_EXTENSION_V11)

    # Projection extension for assets
    proj_attrs = ProjectionExtension.ext(item, add_if_missing=True)
    # Set CRS details globally if they are the same for COG and GRIB or only one of them is exposed.
    # Otherwise, we set the CRS information in the asset
    if epsg == 0 or nocog or nogrib:
        proj_attrs.epsg = None
        proj_attrs.projjson = constants.PROJJSON
    else:
        # Item validation fails if proj:epsg is not in the items due to a bug in the schema of the
        # projection extension, see https://github.com/stac-extensions/projection/issues/7
        # So the following line should be removed once the issue has been solved.
        proj_attrs.epsg = None

    def create_asset(
        href: str,
        media_type: str,
        roles: List[str],
        band: Dict[str, Any],
        crs: Union[Dict[str, Any], int],
        title: str,
    ) -> Asset:
        asset = Asset(href=href, media_type=media_type, roles=roles, title=title)

        isGRIB2 = media_type == constants.GRIB2_MEDIATYPE

        shape = None
        transform = None
        with rasterio.open(href) as dataset:
            if dataset.transform:
                transform = list(dataset.transform)[0:6]

            if len(dataset.shape) == 2:
                shape = [dataset.shape[1], dataset.shape[0]]

            data = dataset.read()
            valid_data = np.ma.masked_array(data, mask=(data < 0))  # type: ignore

            band["statistics"] = {
                "minimum": float(np.nanmin(valid_data)),
                "maximum": float(np.nanmax(valid_data)),
            }

            classes = []
            if isGRIB2:
                if np.any(data == -1.0):
                    classes.append(constants.GRIB2_CLASSIFICATION[0])
                if np.any(data == -3.0):
                    classes.append(constants.GRIB2_CLASSIFICATION[1])
                # some old files contain -999 as nodata value
                if np.any(data == -999.0):
                    classes.append(constants.GRIB2_CLASSIFICATION[2])
            elif np.any(data == -1.0):
                classes.append(constants.COG_CLASSIFICATION)

            if len(classes) > 0:
                band["classification:classes"] = classes
                # Add this if it gets accepted in v1.2:
                # see https://github.com/stac-extensions/classification/pull/34
                # band["classification:incomplete"] = True
            if len(classes) == 1:
                band["nodata"] = band["classification:classes"][0]["value"]

        proj_attrs = ProjectionExtension.ext(asset, add_if_missing=False)
        if shape:
            proj_attrs.shape = shape

        if transform:
            proj_attrs.transform = transform

        if epsg > 0 and not nogrib and not nocog:
            if isinstance(crs, int):
                proj_attrs.epsg = crs
            else:
                proj_attrs.epsg = None
                proj_attrs.projjson = crs

        asset.extra_fields["raster:bands"] = [band]

        return asset

    if basics.gzip:
        asset_href = cog.decompress(asset_href)

    if not nocog:
        epsg_string = "epsg:" + str(epsg) if epsg > 0 else None
        crs: Union[Dict[str, Any], int] = epsg if epsg > 0 else constants.PROJJSON
        cog_href = cog.convert(asset_href, reproject_to=epsg_string)

        band = create_band()

        asset = create_asset(
            cog_href,
            MediaType.COG,
            constants.COG_ROLES,
            band,
            crs,
            constants.ASSET_COG_TITLE,
        )
        item.add_asset(constants.ASSET_COG_KEY, asset)

    if not nogrib:
        band = create_band()

        asset = create_asset(
            asset_href,
            constants.GRIB2_MEDIATYPE,
            constants.GRIB2_ROLES,
            band,
            constants.PROJJSON,
            constants.ASSET_GRIB2_TITLE,
        )
        item.add_asset(constants.ASSET_GRIB2_KEY, asset)

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


def create_band() -> Dict[str, Any]:
    band: Dict[str, Any] = {}
    band["spatial_resolution"] = constants.RESOLUTION_M
    band["unit"] = constants.UNIT
    band["data_type"] = DataType.FLOAT64
    return band
