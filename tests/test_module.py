import unittest

import stactools.noaa_mrms_qpe


class TestModule(unittest.TestCase):
    def test_version(self) -> None:
        self.assertIsNotNone(stactools.noaa_mrms_qpe.__version__)
