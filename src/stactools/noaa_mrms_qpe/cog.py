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


def convert(
    href: str, unzip: bool = False, reproject_to: Union[str, None] = None
) -> str:
    with TemporaryDirectory() as tmp_dir:
        print(f"working in temp folder {tmp_dir}")

        if unzip:
            print(f"unzipping {href}")
            href = decompress(href, tmp_dir)

        if reproject_to:
            print(f"reprojecting {href}")
            reprojected_path = os.path.join(tmp_dir, "reprojected.tif")
            href = reproject(href, reprojected_path, reproject_to)

        print(f"cogifying {href}")

        cog_path = os.path.splitext(href)[0] + ".tif"
        cogify(href, cog_path)
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return cog_path


def decompress(input_path: str, tmp_dir: Union[str, None] = None) -> str:
    if tmp_dir is None:
        output_path = os.path.splitext(input_path)[0]
    else:
        output_path = os.path.join(
            tmp_dir, os.path.splitext(os.path.basename(input_path))[0]
        )

    with gzip.open(input_path, "rb") as f_in:
        with open(output_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    return output_path


def reproject(input_path: str, output_path: str, crs: str) -> str:
    call(["gdalwarp", "-t_srs", crs, input_path, output_path])
    return output_path
