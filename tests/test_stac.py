import unittest

from stactools.noaa_mrms_qpe import stac


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
        id = "MRMS_MultiSensor_QPE_24H_Pass2_00.00_20220530-120000"

        # Write tests for each for the creation of STAC Items
        # Create the STAC Item...
        item = stac.create_item(f"{id}.grib2")

        # Check that it has some required attributes
        self.assertEqual(item.id, f"CONUS_{id}")

        # Validate
        item.validate()
