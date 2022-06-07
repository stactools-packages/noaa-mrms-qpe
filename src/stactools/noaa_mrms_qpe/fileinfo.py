from dataclasses import dataclass
from datetime import datetime


@dataclass
class FileInfo:
    """Class to represent information extracted from a file."""

    id: str
    period: int
    pass_no: int
    datetime: datetime
    gzip: bool = False
