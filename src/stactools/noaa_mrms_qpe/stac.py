import logging
from datetime import datetime, timezone

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

from . import constants

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


def create_item(asset_href: str) -> Item:
    """Create a STAC Item

    This function should include logic to extract all relevant metadata from an
    asset, metadata asset, and/or a constants.py file.

    See `Item<https://pystac.readthedocs.io/en/latest/api.html#item>`_.

    Args:
        asset_href (str): The HREF pointing to an asset associated with the item

    Returns:
        Item: STAC Item object
    """

    properties = {
        "title": "A dummy STAC Item",
        "description": "Used for demonstration purposes",
    }

    demo_geom = {
        "type": "Polygon",
        "coordinates": [[[-180, -90], [180, -90], [180, 90], [-180, 90], [-180, -90]]],
    }

    # Time must be in UTC
    demo_time = datetime.now(tz=timezone.utc)

    item = Item(
        stac_extensions=[constants.EXTENSION],
        id="my-item-id",
        properties=properties,
        geometry=demo_geom,
        bbox=[-180, 90, 180, -90],
        datetime=demo_time,
    )

    # It is a good idea to include proj attributes to optimize for libs like stac-vrt
    proj_attrs = ProjectionExtension.ext(item, add_if_missing=True)
    proj_attrs.epsg = 4326
    proj_attrs.bbox = [-180, 90, 180, -90]
    proj_attrs.shape = [1, 1]  # Raster shape
    proj_attrs.transform = [-180, 360, 0, 90, 0, 180]  # Raster GeoTransform

    # Add an asset to the item (COG for example)
    item.add_asset(
        "image",
        Asset(
            href=asset_href,
            media_type=MediaType.COG,
            roles=["data"],
            title="A dummy STAC Item COG",
        ),
    )

    return item
