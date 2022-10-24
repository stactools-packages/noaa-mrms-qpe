import stactools.core
from stactools.cli.registry import Registry

from stactools.noaa_mrms_qpe.stac import create_collection, create_item

__all__ = ["create_collection", "create_item"]

stactools.core.use_fsspec()


def register_plugin(registry: Registry) -> None:
    from stactools.noaa_mrms_qpe import commands

    registry.register_subcommand(commands.create_noaa_mrms_qpe_command)


__version__ = "0.3.0"
