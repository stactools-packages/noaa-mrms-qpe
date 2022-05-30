import unittest

from stactools.noaa_mrms_qpe import stac


class StacTest(unittest.TestCase):
    def test_create_collection(self) -> None:
        # Write tests for each for the creation of a STAC Collection
        # Create the STAC Collection...
        collection = stac.create_collection(period=1, pass_no=1)
        collection.set_self_href("")

        # Check that it has some required attributes
        self.assertEqual(collection.id, "my-collection-id")
        # self.assertEqual(collection.other_attr...

        # Validate
        collection.validate()

    def test_create_item(self) -> None:
        # Write tests for each for the creation of STAC Items
        # Create the STAC Item...
        item = stac.create_item("/path/to/asset.tif")

        # Check that it has some required attributes
        self.assertEqual(item.id, "my-item-id")
        # self.assertEqual(item.other_attr...

        # Validate
        item.validate()
