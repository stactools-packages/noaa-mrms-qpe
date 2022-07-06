import json
import os.path
import shutil
from tempfile import TemporaryDirectory
from typing import Callable, List

from click import Command, Group
from deepdiff import DeepDiff
from stactools.testing.cli_test import CliTestCase

from stactools.noaa_mrms_qpe.commands import create_noaa_mrms_qpe_command


class CommandsTest(CliTestCase):
    def create_subcommand_functions(self) -> List[Callable[[Group], Command]]:
        return [create_noaa_mrms_qpe_command]

    def test_create_collection(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            src_folder = "./tests/data-files/"
            src_file = os.path.join(src_folder, "collection-1-1.json")
            destination = os.path.join(tmp_dir, "collection-1-1.json")
            period = 1
            pass_no = 1

            result = self.run_command(
                f"noaa-mrms-qpe create-collection {destination} "
                f"--period {period} --pass_no {pass_no} --start_time 2022-01-01T00:00:00Z"
            )

            self.assertEqual(result.exit_code, 0, msg="\n{}".format(result.output))

            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)

            collection = {}
            truth_collection = {}
            with open(destination) as f:
                collection = json.load(f)
            with open(src_file) as f:
                truth_collection = json.load(f)

            self.assertEqual(collection["id"], f"noaa-mrms-qpe-{period}h-pass{pass_no}")

            diff = DeepDiff(
                collection,
                truth_collection,
                ignore_order=True,
                exclude_regex_paths=r"root\['links'\]\[\d+\]\['href'\]",
            )
            self.assertEqual(diff, {})

    def test_create_item(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            id = "MRMS_MultiSensor_QPE_01H_Pass1_00.00_20220601-120000"
            aoi = "GUAM"
            src_folder = f"./tests/data-files/{aoi}"
            src_data_filename = f"{id}.grib2.gz"
            stac_filename = f"{id}.json"

            src_data_file = os.path.join(src_folder, src_data_filename)
            dest_data_file = os.path.join(tmp_dir, src_data_filename)
            shutil.copyfile(src_data_file, dest_data_file)

            src_stac = os.path.join(src_folder, stac_filename)
            dest_stac = os.path.join(tmp_dir, stac_filename)

            result = self.run_command(
                f"noaa-mrms-qpe create-item {dest_data_file} {dest_stac} --aoi {aoi}"
            )
            self.assertEqual(result.exit_code, 0, msg="\n{}".format(result.output))

            files = os.listdir(tmp_dir)
            jsons = [p for p in files if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)

            item = {}
            truth_item = {}
            with open(dest_stac) as f:
                item = json.load(f)
            with open(src_stac) as f:
                truth_item = json.load(f)

            self.assertEqual(item["id"], f"{aoi}_{id}")

            diff = DeepDiff(
                item,
                truth_item,
                ignore_order=True,
                exclude_paths=[
                    "root['assets']['cog']['href']",
                    "root['assets']['grib2']['href']",
                ],
            )
            self.assertEqual(diff, {})
