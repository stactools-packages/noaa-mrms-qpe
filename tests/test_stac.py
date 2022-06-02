import unittest

from stactools.noaa_mrms_qpe import stac

STAC_VERSION = "1.0.0"


class StacTest(unittest.TestCase):
    def test_create_collection(self) -> None:
        # Write tests for each for the creation of a STAC Collection
        # Create the STAC Collection...
        collection = stac.create_collection(period=3, pass_no=2)
        collection.set_self_href("")

        # Check that it has some required attributes
        self.assertEqual(collection.id, "noaa-mrms-qpe-3h-pass2")

        # Validate
        collection.validate()

    def test_create_item(self) -> None:
        folder = "GUAM"
        id = "MRMS_MultiSensor_QPE_01H_Pass1_00.00_20220601-120000"

        # Write tests for each for the creation of STAC Items
        # Create the STAC Item...
        item = stac.create_item(f"./tests/{folder}/{id}.grib2.gz", aoi=folder)

        # Check that it has some required attributes
        self.assertEqual(item.id, f"{folder}_{id}")

        # Validate
        item.validate()
