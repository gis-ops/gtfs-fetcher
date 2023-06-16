import pathlib
from typing import Optional

import typer

from ..feed_sources import feed_sources
from ..utils.constants import LOG
from ..utils.geom import Bbox


def check_bbox(bbox: str) -> Optional[Bbox]:
    if bbox is None:
        return
    try:
        min_x, min_y, max_x, max_y = [float(coord) for coord in bbox.split(",")]
    except ValueError as e:
        err_message = e.args[0]
        if "could not convert" in err_message:
            raise typer.BadParameter("Please pass only numbers as bbox values!")
        elif "not enough values to unpack" in err_message:
            raise typer.BadParameter(
                "Please pass bbox as a string separated by commas like this: min_x,min_y,max_x,max_y"
            )
        else:
            raise typer.BadParameter(f"Unhandled exception: {e}")

    if min_x == max_x or min_y == max_y:
        raise typer.BadParameter("Area cannot be zero! Please pass a valid bbox.")

    return Bbox(min_x, min_y, max_x, max_y)


def check_sources(sources: str) -> Optional[str]:
    """Check if the sources are valid."""
    if sources is None:
        return
    sources = sources.split(",")
    for source in sources:
        if not any(src.__name__.lower() == source.lower() for src in feed_sources):
            raise typer.BadParameter(f"{source} is not a valid feed source!")

    return ",".join(sources)


def check_output_dir(output_dir: str) -> pathlib.Path:
    """Check if the output directory is valid."""
    path = pathlib.Path.cwd() / "feeds"

    if output_dir != "feeds":
        path = pathlib.Path.cwd() / output_dir[1:] if output_dir.startswith("/") else output_dir

    if pathlib.Path.exists(path):
        LOG.info(f"Output directory {path} already exists.")
    else:
        LOG.info(f"Output directory {path} does not exist, will create it.")
        pathlib.Path.mkdir(path, parents=True)

    return path
