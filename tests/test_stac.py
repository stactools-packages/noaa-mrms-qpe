import unittest
from datetime import datetime, timezone
from typing import Any, Dict

from stactools.noaa_mrms_qpe import stac

PERIODS = [1, 3, 6, 12, 24, 48, 72]
PASS_NUMBERS = [1, 2]

COG_MEDIATYPE = "image/tiff; application=geotiff; profile=cloud-optimized"
GRIB_MEDIATYPE = "application/wmo-GRIB2"

TEST_FILES = [
    [
        "ALASKA",
        "MRMS_MultiSensor_QPE_12H_Pass2_00.00_20220602-000000",
        12,
        2,
        [2022, 6, 2, 0],
        True,
    ],
    [
        "CARIB",
        "MRMS_MultiSensor_QPE_24H_Pass2_00.00_20220602-030000",
        24,
        2,
        [2022, 6, 2, 3],
        True,
    ],
    [
        "CONUS",
        "MRMS_MultiSensor_QPE_01H_Pass2_00.00_20220602-120000",
        1,
        2,
        [2022, 6, 2, 12],
        True,
    ],
    [
        "GUAM",
        "MRMS_MultiSensor_QPE_01H_Pass1_00.00_20220601-120000",
        1,
        1,
        [2022, 6, 1, 12],
        True,
    ],
    [
        "HAWAII",
        "MRMS_MultiSensor_QPE_72H_Pass2_00.00_20220601-230000",
        72,
        2,
        [2022, 6, 1, 23],
        False,
    ],
]


class StacTest(unittest.TestCase):
    def test_create_collection(self) -> None:
        for period in PERIODS:
            for pass_no in PASS_NUMBERS:
                with self.subTest(period=period, pass_no=pass_no):
                    collection = stac.create_collection(period=period, pass_no=pass_no)
                    collection.set_self_href("")

                    collection_dict = collection.to_dict()

                    self.assertEqual(
                        collection.summaries.get_list("noaa_mrms_qpe:pass"), [pass_no]
                    )
                    self.assertEqual(
                        collection.summaries.get_list("noaa_mrms_qpe:period"), [period]
                    )

                    # self.assertTrue("item_assets" in collection)
                    # self.assertTrue("data" in collection["item_assets"])

                    assets: Dict[str, Dict[str, Any]] = collection_dict["item_assets"]
                    self.assertEqual(len(assets), 2)

                    # Check COG asset
                    cog_asset = assets["cog"]
                    self.assertEqual(cog_asset["type"], COG_MEDIATYPE)
                    self.assertTrue("raster:bands" in cog_asset)
                    self.assertEqual(len(cog_asset["raster:bands"]), 1)
                    cog_band = cog_asset["raster:bands"][0]
                    self.assertEqual(cog_band["spatial_resolution"], 1000)
                    self.assertEqual(cog_band["unit"], "mm")
                    self.assertEqual(cog_band["data_type"], "float64")
                    self.assertFalse("classification:classes" in cog_band)
                    self.assertFalse("nodata" in cog_band)

                    # Check GRIB2 asset
                    grib_asset = assets["grib2"]
                    self.assertEqual(grib_asset["type"], GRIB_MEDIATYPE)
                    self.assertTrue("raster:bands" in grib_asset)
                    self.assertEqual(len(grib_asset["raster:bands"]), 1)
                    grib_band = grib_asset["raster:bands"][0]
                    self.assertEqual(grib_band["spatial_resolution"], 1000)
                    self.assertEqual(grib_band["unit"], "mm")
                    self.assertEqual(grib_band["data_type"], "float64")
                    self.assertFalse("classification:classes" in grib_band)
                    self.assertFalse("nodata" in grib_band)

                    # todo check item assets

                    collection.validate()

    def test_create_item(self) -> None:
        for test_data in TEST_FILES:
            with self.subTest(test_data=test_data):
                folder, id, period, pass_no, dt, gzip = test_data

                file = f"{id}.grib2"
                if gzip:
                    file += ".gz"

                item = stac.create_item(f"./tests/{folder}/{file}", aoi=folder)  # type: ignore

                self.assertEqual(item.id, f"{folder}_{id}")
                self.assertEqual(item.properties["noaa_mrms_qpe:pass"], pass_no)
                self.assertEqual(item.properties["noaa_mrms_qpe:period"], period)
                ref_dt = datetime(
                    dt[0], dt[1], dt[2], dt[3], 0, 0, 0, tzinfo=timezone.utc  # type: ignore
                )
                self.assertEqual(item.datetime, ref_dt)
                self.assertEqual(len(item.assets), 2)

                # Check COG asset
                cog_asset = item.assets["cog"].to_dict()
                self.assertEqual(cog_asset["type"], COG_MEDIATYPE)
                self.assertTrue("raster:bands" in cog_asset)
                self.assertEqual(len(cog_asset["raster:bands"]), 1)
                cog_band = cog_asset["raster:bands"][0]
                self.assertEqual(cog_band["spatial_resolution"], 1000)
                self.assertEqual(cog_band["unit"], "mm")
                self.assertEqual(cog_band["data_type"], "float64")
                # self.assertTrue("classification:classes" in cog_band)
                # self.assertEqual(len(cog_band["classification:classes"]), 1)
                # self.assertEqual(cog_band["nodata"], -1)

                # Check GRIB2 asset
                grib_asset = item.assets["grib2"].to_dict()
                self.assertEqual(grib_asset["type"], GRIB_MEDIATYPE)
                self.assertTrue("raster:bands" in grib_asset)
                self.assertEqual(len(grib_asset["raster:bands"]), 1)
                grib_band = grib_asset["raster:bands"][0]
                self.assertEqual(grib_band["spatial_resolution"], 1000)
                self.assertEqual(grib_band["unit"], "mm")
                self.assertEqual(grib_band["data_type"], "float64")
                # self.assertTrue("classification:classes" in grib_band)
                # self.assertEqual(len(grib_band["classification:classes"]), 1)
                # self.assertEqual(grib_band["nodata"], -999)

                item.validate()
