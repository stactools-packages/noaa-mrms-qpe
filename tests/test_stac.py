import os.path
import shutil
import unittest
from datetime import datetime, timezone
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Optional

from pystac import Collection, Item

from stactools.noaa_mrms_qpe import constants, stac

PERIODS: List[int] = [1, 3, 6, 12, 24, 48, 72]
PASS_NUMBERS: List[int] = [1, 2]

COG_MEDIATYPE: str = "image/tiff; application=geotiff; profile=cloud-optimized"
GRIB_MEDIATYPE: str = "application/wmo-GRIB2"

TEST_COLLECTIONS: List[Dict[str, Any]] = []
for period in PERIODS:
    for pass_no in PASS_NUMBERS:
        for nocog in [True, False]:
            for nogrib in [True, False]:
                TEST_COLLECTIONS.append(
                    {
                        "period": period,
                        "pass_no": pass_no,
                        "nocog": nocog,
                        "nogrib": nogrib,
                    }
                )

TEST_FILES: List[List[Any]] = [
    [
        "ALASKA",  # aoi
        "MRMS_MultiSensor_QPE_12H_Pass2_00.00_20220602-000000",  # filename
        12,  # period
        2,  # pass no
        [2022, 6, 2, 0],  # datetime
        True,  # gzip
        True,  # nocog
        True,  # nogrib
        None,  # collection path
        False,  # has nodata values
    ],
    [
        "CARIB",
        "MRMS_MultiSensor_QPE_24H_Pass2_00.00_20220602-030000",
        24,
        2,
        [2022, 6, 2, 3],
        True,
        3857,
        False,
        None,
        True,
    ],
    [
        "CONUS",
        "MRMS_MultiSensor_QPE_01H_Pass2_00.00_20220602-120000",
        1,
        2,
        [2022, 6, 2, 12],
        True,
        False,
        False,
        None,
        False,
    ],
    [
        "GUAM",
        "MRMS_MultiSensor_QPE_01H_Pass1_00.00_20220601-120000",
        1,
        1,
        [2022, 6, 1, 12],
        True,
        False,
        False,
        "./tests/data-files/collection-1-1.json",
        True,
    ],
    [
        "HAWAII",
        "MRMS_MultiSensor_QPE_72H_Pass2_00.00_20220601-230000",
        72,
        2,
        [2022, 6, 1, 23],
        False,
        True,
        False,
        None,
        False,
    ],
]


class StacTest(unittest.TestCase):
    def test_create_collection(self) -> None:
        for test_data in TEST_COLLECTIONS:
            with self.subTest(test_data=test_data):
                period: int = test_data["period"]
                pass_no: int = test_data["pass_no"]
                nocog: bool = test_data["nocog"]
                nogrib: bool = test_data["nogrib"]

                # untested right now: parameters start_time, thumbnail
                collection = stac.create_collection(
                    period=period, pass_no=pass_no, nocog=nocog, nogrib=nogrib
                )
                collection.set_self_href("")

                collection.validate()

                collection_dict = collection.to_dict()

                self.assertEqual(
                    collection.summaries.get_list("noaa_mrms_qpe:pass"), [pass_no]
                )
                self.assertEqual(
                    collection.summaries.get_list("noaa_mrms_qpe:period"), [period]
                )

                self.assertTrue("item_assets" in collection_dict)
                assets: Dict[str, Dict[str, Any]] = collection_dict["item_assets"]

                asset_count = 2
                if nocog:
                    asset_count -= 1
                if nogrib:
                    asset_count -= 1
                self.assertEqual(len(assets), asset_count)

                # Check COG asset
                if nocog:
                    self.assertFalse("cog" in assets)
                else:
                    self.assertTrue("cog" in assets)
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
                if nogrib:
                    self.assertFalse("grib2" in assets)
                else:
                    self.assertTrue("grib2" in assets)
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

    def test_create_item(self) -> None:
        for test_data in TEST_FILES:
            with self.subTest(test_data=test_data):
                folder: str = test_data[0]
                id: str = test_data[1]
                period: int = test_data[2]
                pass_no: int = test_data[3]
                dt: List[int] = test_data[4]
                gzip: bool = test_data[5]
                nocog: bool = False
                epsg: int = 0
                if isinstance(test_data[6], bool):
                    nocog = test_data[6]
                else:
                    epsg = test_data[6]
                nogrib: bool = test_data[7]
                collection_path: Optional[str] = test_data[8]
                nodata: bool = test_data[9]
                proj_toplevel: bool = epsg == 0 or nogrib or nocog

                src_dir = f"./tests/data-files/{folder}"
                filename = f"{id}.grib2"
                if gzip:
                    filename += ".gz"

                item: Optional[Item] = None
                with TemporaryDirectory() as tmp_dir:
                    src_data_file = os.path.join(src_dir, filename)
                    dest_data_file = os.path.join(tmp_dir, filename)
                    shutil.copyfile(src_data_file, dest_data_file)

                    collection = None
                    if collection_path is not None:
                        collection = Collection.from_file(collection_path)

                    item = stac.create_item(
                        dest_data_file,
                        aoi=constants.AOI[folder],
                        nogrib=nogrib,
                        nocog=nocog,
                        collection=collection,
                        epsg=epsg,
                    )

                item.validate()

                self.assertIsNotNone(item)
                self.assertEqual(item.id, f"{folder}_{id}")
                self.assertEqual(item.properties["noaa_mrms_qpe:pass"], pass_no)
                self.assertEqual(item.properties["noaa_mrms_qpe:period"], period)
                self.assertEqual(
                    item.properties["noaa_mrms_qpe:region"], constants.AOI[folder]
                )
                self.assertTrue("description" in item.properties)
                ref_dt = datetime(
                    dt[0], dt[1], dt[2], dt[3], 0, 0, 0, tzinfo=timezone.utc
                )
                self.assertEqual(item.datetime, ref_dt)

                self.assertEqual("proj:projjson" in item.properties, proj_toplevel)
                self.assertIsNone(item.properties["proj:epsg"])
                if proj_toplevel:
                    self.assertIsInstance(item.properties["proj:projjson"], dict)

                if collection is not None:
                    self.assertEqual(item.collection_id, collection.id)
                else:
                    self.assertIsNone(item.collection_id)

                asset_count = 2
                if nocog:
                    asset_count -= 1
                if nogrib:
                    asset_count -= 1
                self.assertEqual(len(item.assets), asset_count)

                # Check COG asset
                if nocog:
                    self.assertFalse("cog" in item.assets)
                else:
                    cog_asset = item.assets["cog"].to_dict()
                    self.assertEqual(cog_asset["type"], COG_MEDIATYPE)
                    self.assertTrue("title" in cog_asset)
                    self.assertEqual(len(cog_asset["roles"]), 2)
                    self.assertEqual(len(cog_asset["proj:shape"]), 2)
                    self.assertEqual(len(cog_asset["proj:transform"]), 6)
                    self.assertEqual("proj:epsg" in cog_asset, not proj_toplevel)
                    if not proj_toplevel:
                        if epsg > 0:
                            self.assertEqual(cog_asset["proj:epsg"], epsg)
                        else:
                            self.assertIsNone(cog_asset["proj:epsg"])
                            self.assertIsInstance(cog_asset["proj:projjson"], dict)

                    self.assertTrue("raster:bands" in cog_asset)
                    self.assertEqual(len(cog_asset["raster:bands"]), 1)
                    cog_band = cog_asset["raster:bands"][0]
                    self.assertEqual(cog_band["spatial_resolution"], 1000)
                    self.assertEqual(cog_band["unit"], "mm")
                    self.assertEqual(cog_band["data_type"], "float64")

                    self.assertTrue("statistics" in cog_band)
                    self.assertEqual(cog_band["statistics"]["minimum"], 0)
                    self.assertGreaterEqual(cog_band["statistics"]["maximum"], 0)

                    self.assertEqual("classification:classes" in cog_band, nodata)
                    if nodata:
                        self.assertEqual(len(cog_band["classification:classes"]), 1)
                        class1 = cog_band["classification:classes"][0]
                        self.assertEqual(class1["value"], -1.0)
                        self.assertTrue("name" in class1)
                        self.assertTrue("description" in class1)
                        self.assertTrue(class1["nodata"])

                        self.assertEqual(cog_band["nodata"], -1.0)

                # Check GRIB2 asset
                if nogrib:
                    self.assertFalse("grib2" in item.assets)
                else:
                    grib_asset = item.assets["grib2"].to_dict()
                    self.assertEqual(grib_asset["type"], GRIB_MEDIATYPE)
                    self.assertTrue("title" in grib_asset)
                    self.assertEqual(len(grib_asset["roles"]), 2)
                    self.assertEqual(len(grib_asset["proj:shape"]), 2)
                    self.assertEqual(len(grib_asset["proj:transform"]), 6)
                    self.assertEqual("proj:epsg" in grib_asset, not proj_toplevel)
                    self.assertEqual("proj:projjson" in grib_asset, not proj_toplevel)
                    if not proj_toplevel:
                        self.assertIsNone(grib_asset["proj:epsg"])
                        self.assertIsInstance(grib_asset["proj:projjson"], dict)

                    self.assertTrue("raster:bands" in grib_asset)
                    self.assertEqual(len(grib_asset["raster:bands"]), 1)
                    grib_band = grib_asset["raster:bands"][0]
                    self.assertEqual(grib_band["spatial_resolution"], 1000)
                    self.assertEqual(grib_band["unit"], "mm")
                    self.assertEqual(grib_band["data_type"], "float64")

                    self.assertTrue("statistics" in grib_band)
                    self.assertEqual(grib_band["statistics"]["minimum"], 0)
                    self.assertGreaterEqual(grib_band["statistics"]["maximum"], 0)

                    self.assertEqual("classification:classes" in grib_band, nodata)
                    if nodata:
                        self.assertGreaterEqual(
                            len(grib_band["classification:classes"]), 1
                        )
                        class1 = grib_band["classification:classes"][0]
                        self.assertIn(class1["value"], [-1.0, -3.0, -999.0])
                        self.assertTrue("name" in class1)
                        self.assertTrue("description" in class1)
                        self.assertTrue(class1["nodata"])

                        if len(grib_band["classification:classes"]) == 1:
                            self.assertTrue("nodata" in grib_band)
