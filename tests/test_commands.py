import os.path
from tempfile import TemporaryDirectory
from typing import Callable, List

import pystac
from click import Command, Group
from stactools.testing.cli_test import CliTestCase

from stactools.ephemeral.commands import create_ephemeralcmd_command


class CommandsTest(CliTestCase):
    def create_subcommand_functions(self) -> List[Callable[[Group], Command]]:
        return [create_ephemeralcmd_command]

    def test_create_collection(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            # Run your custom create-collection command and validate

            # Example:
            destination = os.path.join(tmp_dir, "collection.json")

            result = self.run_command(f"ephemeralcmd create-collection {destination}")

            self.assertEqual(result.exit_code, 0, msg="\n{}".format(result.output))

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)

            collection = pystac.read_file(destination)
            self.assertEqual(collection.id, "my-collection-id")
            # self.assertEqual(item.other_attr...

            collection.validate()

    def test_create_item(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            # Run your custom create-item command and validate

            # Example:
            infile = "/path/to/asset.tif"
            destination = os.path.join(tmp_dir, "item.json")
            result = self.run_command(
                f"ephemeralcmd create-item {infile} {destination}"
            )
            self.assertEqual(result.exit_code, 0, msg="\n{}".format(result.output))

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)

            item = pystac.read_file(destination)
            self.assertEqual(item.id, "my-item-id")
            # self.assertEqual(item.other_attr...

            item.validate()
