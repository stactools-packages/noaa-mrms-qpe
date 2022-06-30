import gzip
import logging
import os
import shutil
from tempfile import TemporaryDirectory
from typing import List, Optional

from stactools.core.utils.subprocess import call

from . import constants

logger = logging.getLogger(__name__)


def convert(
    href: str, unzip: bool = False, reproject_to: Optional[str] = None
) -> List[str]:

    dir = os.path.dirname(href)
    name = os.path.splitext(os.path.basename(href))[0]
    if unzip:
        name = os.path.splitext(name)[0]
    mask_name = name + "-mask.tif"
    name = name + ".tif"

    with TemporaryDirectory() as tmp_dir:
        if unzip:
            href = decompress(href, tmp_dir)

        if reproject_to:
            href = reproject(href, os.path.join(tmp_dir, name), reproject_to)

        href, output_mask_path = cogify(
            href, os.path.join(dir, name), os.path.join(dir, mask_name)
        )

    return [href, output_mask_path]


def decompress(input_path: str, tmp_dir: Optional[str] = None) -> str:
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


def cogify(input_path: str, output_path: str, output_mask_path: str) -> List[str]:
    print(f"cogifying {input_path} to {output_path} and {output_mask_path}")
    call(
        [
            "gdal_calc.py",
            "-A",
            input_path,
            "--outfile",
            output_path,
            "--overwrite",
            "--calc",
            f"maximum(A, {constants.COG_DATA_NODATA})",
            "--NoDataValue",
            str(constants.COG_DATA_NODATA),
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
    call(
        [
            "gdal_calc.py",
            "-A",
            input_path,
            "--outfile",
            output_mask_path,
            "--overwrite",
            "--calc",
            f"minimum(A, {constants.COG_MASK_NODATA})",
            "--NoDataValue",
            str(constants.COG_MASK_NODATA),
            "--type",
            "Int16",
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
    hrefs: List[str] = [output_path, output_mask_path]
    return hrefs
