import logging
import time
from enum import Enum

from rich.progress import Progress, SpinnerColumn, TextColumn


class Predicate(str, Enum):
    intersects = "intersects"
    contains = "contains"


class Feed(str, Enum):
    new_available = "new_available"
    new_not_available = "new_not_available"
    info_missing = "info_missing"


def spinner(text: str, timer: int) -> None:
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description=text, total=None)
        time.sleep(timer)


logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger()

# format time checks like last-modified header
TIMECHECK_FMT = "%a, %d %b %Y %H:%M:%S GMT"
