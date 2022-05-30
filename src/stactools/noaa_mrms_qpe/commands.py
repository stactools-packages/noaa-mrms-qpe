import logging

import click
from click import Command, Group

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
        help='A custom collection ID, defaults to "noaa-mrms-qpe-{t}h-pass{p}"',
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
    def create_item_command(source: str, destination: str) -> None:
        """Creates a STAC Item

        Args:
            source (str): HREF of the Asset associated with the Item
            destination (str): An HREF for the STAC Collection
        """
        item = stac.create_item(source)

        item.save_object(dest_href=destination)

        return None

    return noaa_mrms_qpe
