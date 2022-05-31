import gzip
import logging
import os
import shutil
from tempfile import TemporaryDirectory
from typing import Union

from stactools.core.utils.convert import cogify
from stactools.core.utils.subprocess import call

logger = logging.getLogger(__name__)

# todo: This doesn't respect the no-data values,
# check how we can set -1 and -3 as no-data values for the GRIB files
# so that the COGs set their own no-data values correctly

# gdal_calc.py -A MRMS_MultiSensor_QPE_24H_Pass2_00.00_20220530-120000.grib2
#   --outfile=cog.tif --calc="A*(A>=0)" --NoDataValue=-1
#   --format=COG --co="TARGET_SRS=EPSG:3857" --co="COMPRESS=DEFLATE"
# ERROR 6: GDALDriver::Create() ... no create method implemented for this format.
# 'NoneType' object has no attribute 'SetGeoTransform'


def convert(
    href: str, unzip: bool = False, reproject_to: Union[str, None] = None
) -> str:

    dir = os.path.dirname(href)
    name = os.path.splitext(os.path.basename(href))[0]
    if unzip:
        name = os.path.splitext(name)[0]
    name = name + ".tif"

    with TemporaryDirectory() as tmp_dir:
        if unzip:
            href = decompress(href, tmp_dir)

        if reproject_to:
            href = reproject(href, os.path.join(tmp_dir, name), reproject_to)

        target = os.path.join(dir, name)
        print(f"cogifying {href} to {target}")
        cogify(href, target)

        shutil.rmtree(tmp_dir, ignore_errors=True)

    return target


def decompress(input_path: str, tmp_dir: Union[str, None] = None) -> str:
    if tmp_dir is None:
        output_path = os.path.splitext(input_path)[0]
    else:
        output_path = os.path.join(
            tmp_dir, os.path.splitext(os.path.basename(input_path))[0]
        )

    print(f"unzipping {input_path} to {output_path}")
    with gzip.open(input_path, "rb") as f_in:
        with open(output_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    return output_path


def reproject(input_path: str, output_path: str, crs: str) -> str:
    print(f"reprojecting {input_path} to {output_path}")
    call(["gdalwarp", "-t_srs", crs, input_path, output_path])
    return output_path
