import os.path
from tempfile import TemporaryDirectory
from typing import Callable, List

import pystac
from click import Command, Group
from stactools.testing.cli_test import CliTestCase

from stactools.noaa_mrms_qpe.commands import create_noaa_mrms_qpe_command


class CommandsTest(CliTestCase):
    def create_subcommand_functions(self) -> List[Callable[[Group], Command]]:
        return [create_noaa_mrms_qpe_command]

    def test_create_collection(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            # Run your custom create-collection command and validate

            # Example:
            destination = os.path.join(tmp_dir, "collection.json")

            result = self.run_command(f"noaa_mrms_qpe create-collection {destination}")

            self.assertEqual(result.exit_code, 0, msg="\n{}".format(result.output))

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)

            collection = pystac.read_file(destination)
            self.assertEqual(collection.id, "noaa-mrms-qpe-1h-pass1")

            collection.validate()

    def test_create_item(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            # Run your custom create-item command and validate

            # Example:
            id = "MRMS_MultiSensor_QPE_24H_Pass2_00.00_20220530-120000"
            aoi = "HAWAII"
            infile = f"/path/to/{id}.grib2"
            destination = os.path.join(tmp_dir, "item.json")
            result = self.run_command(
                f"noaa_mrms_qpe create-item {infile} {destination} --aoi {aoi}"
            )
            self.assertEqual(result.exit_code, 0, msg="\n{}".format(result.output))

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)

            item = pystac.read_file(destination)
            self.assertEqual(item.id, f"{aoi}_{id}")
            # self.assertEqual(item.other_attr...

            item.validate()
