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
            id = "MRMS_MultiSensor_QPE_01H_Pass1_00.00_20220601-120000"
            folder = "GUAM"
            infile = f"./tests/{folder}/{id}.grib2.gz"
            destination = os.path.join(tmp_dir, "item.json")
            result = self.run_command(
                f"noaa_mrms_qpe create-item {infile} {destination} --aoi {folder} --cog TRUE"
            )
            self.assertEqual(result.exit_code, 0, msg="\n{}".format(result.output))

            files = os.listdir(tmp_dir)
            jsons = [p for p in files if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)

            item = pystac.read_file(destination)
            self.assertEqual(item.id, f"{folder}_{id}")
            # self.assertEqual(item.other_attr...

            item.validate()
