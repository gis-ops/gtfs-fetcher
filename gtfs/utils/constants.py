import logging
import time
from enum import Enum

from rich.progress import Progress, SpinnerColumn, TextColumn


class Predicate(str, Enum):
    intersects = "intersects"
    contains = "contains"


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
