import gzip
import logging
import os
import shutil
from tempfile import TemporaryDirectory
from typing import Optional

from stactools.core.utils.subprocess import call

from . import constants

logger = logging.getLogger(__name__)


def convert(href: str, reproject_to: Optional[str] = None) -> str:
    dir = os.path.dirname(href)
    name = os.path.splitext(os.path.basename(href))[0] + ".tif"

    with TemporaryDirectory() as tmp_dir:
        if reproject_to:
            href = reproject(href, os.path.join(tmp_dir, name), reproject_to)

        href = cogify(href, os.path.join(dir, name))

    return href


def decompress(input_path: str) -> str:
    output_path = os.path.splitext(input_path)[0]

    print(f"unzipping {input_path} to {output_path}")
    with gzip.open(input_path, "rb") as f_in:
        with open(output_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    return output_path


def reproject(input_path: str, output_path: str, crs: str) -> str:
    print(f"reprojecting {input_path} to {output_path}")
    call(["gdalwarp", "-t_srs", crs, input_path, output_path])
    return output_path


def cogify(input_path: str, output_path: str) -> str:
    print(f"cogifying {input_path} to {output_path}")
    call(
        [
            "gdal_calc.py",
            "-A",
            input_path,
            "--outfile",
            output_path,
            "--overwrite",
            "--calc",
            f"maximum(A, {constants.COG_NODATA})",
            "--NoDataValue",
            str(constants.COG_NODATA),
            "--format",
            "GTIFF",  # COG
            "--co",
            "TILED=YES",
            "--co",
            "COPY_SRC_OVERVIEWS=YES",
            "--co",
            f"COMPRESS={constants.COG_COMPRESS}"
            # "--co", f"TARGET_SRS={reproject_to}"
        ]
    )
    return output_path
