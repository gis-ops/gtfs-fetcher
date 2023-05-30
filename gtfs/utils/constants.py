import time
from enum import Enum

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.style import Style


class Predicate(str, Enum):
    intersects = "intersects"
    contains = "contains"


error = Style(color="red", bold=True)
success = Style(color="green", bold=True)
console = Console()


def spinner(text: str, timer: int) -> None:
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description=text, total=None)
        time.sleep(timer)
