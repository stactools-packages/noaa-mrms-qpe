import unittest
from datetime import datetime, timezone

from stactools.noaa_mrms_qpe import stac

PERIODS = [1, 3, 6, 12, 24, 48, 72]
PASS_NUMBERS = [1, 2]

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

                    self.assertEqual(
                        collection.id, f"noaa-mrms-qpe-{period}h-pass{pass_no}"
                    )
                    summaries = collection.summaries.to_dict()
                    self.assertEqual(summaries["noaa_mrms_qpe:pass"], [pass_no])
                    self.assertEqual(summaries["noaa_mrms_qpe:period"], [period])

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
                self.assertEqual(len(item.assets), 1)

                item.validate()
