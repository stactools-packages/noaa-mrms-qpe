import gzip
import logging
import os
import shutil
from tempfile import TemporaryDirectory
from typing import Union

from stactools.core.utils.subprocess import call

from . import constants

logger = logging.getLogger(__name__)


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

        href = cogify(href, os.path.join(dir, name))

        shutil.rmtree(tmp_dir, ignore_errors=True)

    return href


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


def cogify(input_path: str, output_path: str) -> str:
    print(f"cogifying {input_path} to {output_path}")
    call(
        [
            "gdal_calc.py",
            "-A",
            input_path,
            "--outfile",
            output_path,
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
            "COMPRESS=LZW"
            # "--co", f"TARGET_SRS={reproject_to}"
        ]
    )
    return output_path
