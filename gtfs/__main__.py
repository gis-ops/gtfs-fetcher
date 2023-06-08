#!/usr/bin/env python
"""Command line interface for fetching GTFS."""
import logging
from typing import Optional

import typer
from prettytable.colortable import ColorTable, Themes
from typing_extensions import Annotated

from .feed_source import FeedSource
from .feed_sources import feed_sources
from .utils.constants import Predicate, spinner
from .utils.geom import Bbox, bbox_contains_bbox, bbox_intersects_bbox

logging.basicConfig()
LOG = logging.getLogger()
app = typer.Typer()


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


@app.command()
def list_feeds(
    bbox: Annotated[
        Optional[str],
        typer.Option(
            "--bbox",
            "-b",
            help="pass value as a string separated by commas like this: min_x,min_y,max_x,max_y",
            callback=check_bbox,
        ),
    ] = None,
    predicate: Annotated[
        Optional[Predicate],
        typer.Option(
            "--predicate",
            "-pd",
            help="the gtfs feed should intersect or should be contained inside the user's bbox",
        ),
    ] = None,
    pretty: Annotated[
        bool,
        typer.Option(
            "--pretty",
            "-pt",
            help="display feeds inside a pretty table",
        ),
    ] = False,
) -> None:
    """Filter feeds spatially based on bounding box."""
    if bbox is None and predicate is not None:
        raise typer.BadParameter(
            f"Please pass a bbox if you want to filter feeds spatially based on predicate = {predicate}!"
        )
    elif bbox is not None and predicate is None:
        raise typer.BadParameter(
            f"Please pass a predicate if you want to filter feeds spatially based on bbox = {bbox}!"
        )
    else:
        spinner("Fetching feeds...", 1)
        if pretty is True:
            pretty_output = ColorTable(
                ["Feed Source", "Transit URL", "Bounding Box"], theme=Themes.OCEAN, hrules=1
            )

        for src in feed_sources:
            feed_bbox: Bbox = src.bbox
            if bbox is not None and predicate == "contains":
                if not bbox_contains_bbox(feed_bbox, bbox):
                    continue
            elif bbox is not None and predicate == "intersects":
                if (not bbox_intersects_bbox(feed_bbox, bbox)) and (
                    not bbox_intersects_bbox(bbox, feed_bbox)
                ):
                    continue

            if pretty is True:
                pretty_output.add_row(
                    [
                        src.__name__,
                        src.url,
                        [feed_bbox.min_x, feed_bbox.min_y, feed_bbox.max_x, feed_bbox.max_y],
                    ]
                )
                continue

            print(src.url)

        if pretty is True:
            print("\n" + pretty_output.get_string())


@app.command()
def fetch_feeds(sources=None):
    """
    :param sources: List of :FeedSource: modules to fetch; if not set, will fetch all available.
    """
    statuses = {}  # collect the statuses for all the files

    # default to use all of them
    if not sources:
        sources = feed_sources

    LOG.info("Going to fetch feeds from sources: %s", sources)
    for src in sources:
        LOG.debug("Going to start fetch for %s...", src)
        try:
            if issubclass(src, FeedSource):
                inst = src()
                inst.fetch()
                statuses.update(inst.status)
            else:
                LOG.warning(
                    "Skipping class %s, which does not subclass FeedSource.",
                    src.__name__,
                )
        except AttributeError:
            LOG.error("Skipping feed %s, which could not be found.", src)

    # remove last check key set at top level of each status dictionary
    if "last_check" in statuses:
        del statuses["last_check"]

    ptable = ColorTable(
        [
            "file",
            "new?",
            "valid?",
            "current?",
            "newly effective?",
            "error",
        ],
        theme=Themes.OCEAN,
        hrules=1,
    )

    for file_name in statuses:
        stat = statuses[file_name]
        msg = []
        msg.append(file_name)
        msg.append("x" if "is_new" in stat and stat["is_new"] else "")
        msg.append("x" if "is_valid" in stat and stat["is_valid"] else "")
        msg.append("x" if "is_current" in stat and stat["is_current"] else "")
        msg.append("x" if "newly_effective" in stat and stat.get("newly_effective") else "")
        if "error" in stat:
            msg.append(stat["error"])
        else:
            msg.append("")
        ptable.add_row(msg)

    LOG.info("Results:\n%s", ptable.get_string())
    LOG.info("All done!")


if __name__ == "__main__":
    app()
