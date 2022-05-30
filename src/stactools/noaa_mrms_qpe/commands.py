import logging

import click
from click import Command, Group
from pystac import Collection

from stactools.noaa_mrms_qpe import stac

logger = logging.getLogger(__name__)


def create_noaa_mrms_qpe_command(cli: Group) -> Command:
    """Creates the stactools-noaa-mrms-qpe command line utility."""

    @cli.group(
        "noaa_mrms_qpe",
        short_help=("Commands for working with stactools-noaa-mrms-qpe"),
    )
    def noaa_mrms_qpe() -> None:
        pass

    @noaa_mrms_qpe.command(
        "create-collection",
        short_help="Creates a STAC collection",
    )
    @click.argument("destination")
    @click.option(
        "--period",
        default=1,
        help="The time period the sub-product is for, either 1 (default), 3, 6, 12, 24, 48, or 72",
    )
    @click.option(
        "--pass_no",
        default=1,
        help="The pass number of the sub-product, either 1 (default) or 2",
    )
    @click.option(
        "--id",
        default="",
        help="A custom collection ID, defaults to 'noaa-mrms-qpe-{t}h-pass{p}'",
    )
    @click.option(
        "--thumbnail",
        default="",
        help="URL for the collection thumbnail asset (none if empty)",
    )
    def create_collection_command(
        destination: str,
        period: int = 1,
        pass_no: int = 1,
        id: str = "",
        thumbnail: str = "",
    ) -> None:
        """Creates a STAC Collection

        Args:
            destination (str): An HREF for the Collection JSON
        """
        collection = stac.create_collection(period, pass_no, thumbnail)
        if len(id) > 0:
            collection.id = id
        collection.set_self_href(destination)
        collection.save_object()

        return None

    @noaa_mrms_qpe.command("create-item", short_help="Create a STAC item")
    @click.argument("source")
    @click.argument("destination")
    @click.option(
        "--aoi",
        default="CONUS",
        help="The area of interest, either 'ALASKA', 'CONUS' (continental US, default), "
        "'CARIB' (Caribbean islands), 'GUAM' or 'HAWAII'",
    )
    @click.option(
        "--collection",
        default="",
        help="An HREF to the Collection JSON",
    )
    @click.option(
        "--cog",
        default=False,
        help="Converts the GRIB2 file to COG",
    )
    @click.option(
        "--epsg",
        default=0,
        help="Converts the COG files to the given EPSG Code (e.g. 3857)",
    )
    def create_item_command(
        source: str,
        destination: str,
        aoi: str = "CONUS",
        collection: str = "",
        cog: bool = False,
        epsg: int = 0,
    ) -> None:
        """Creates a STAC Item

        Args:
            source (str): HREF of the Asset associated with the Item
            destination (str): An HREF for the STAC Item
        """
        stac_collection = None
        if len(collection) > 0:
            stac_collection = Collection.from_file(collection)

        item = stac.create_item(source, aoi, stac_collection, cog, epsg)
        item.save_object(dest_href=destination)

        return None

    return noaa_mrms_qpe
