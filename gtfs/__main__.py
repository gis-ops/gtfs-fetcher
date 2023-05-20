#!/usr/bin/env python
"""Command line interface for fetching GTFS."""
import logging

import typer
from halo import Halo
from prettytable.colortable import ColorTable, Themes
from typing_extensions import Annotated

from .feed_source import FeedSource
from .feed_sources import __all__ as feed_sources
from .utils.constants import Predicate
from .utils.geom import Bbox, bbox_contains_bbox, bbox_intersects_bbox

LOG = logging.getLogger()
app = typer.Typer()


def check_bbox(bbox: str) -> Bbox:
    try:
        min_x, min_y, max_x, max_y = [float(coord) for coord in bbox.split(",")]
    except ValueError as e:
        if "could not convert" in e.args[0]:
            raise typer.BadParameter("Please pass only numbers as bbox values!")
        elif "not enough values to unpack" in e.args[0]:
            raise typer.BadParameter(
                "Please pass bbox as a string separated by commas like this: min_x,min_y,max_x,max_y"
            )

    if min_x == max_x or min_y == max_y:
        raise typer.BadParameter("Area cannot be zero! Please pass a valid bbox.")

    return Bbox(min_x, min_y, max_x, max_y)


@app.command()
def list_feeds(
    bbox: Annotated[
        str,
        typer.Argument(
            help="pass value as a string separated by commas like this: min_x,min_y,max_x,max_y",
            callback=check_bbox,
        ),
    ],
    predicate: Annotated[
        Predicate,
        typer.Option(
            "--predicate",
            "-p",
            help="the gtfs feed should intersect or should be contained inside the user's bbox",
        ),
    ] = Predicate.intersects,
) -> None:
    """Filter feeds spatially based on bounding box."""
    spinner = Halo(text="Filtering...", text_color="cyan", spinner="dots")
    spinner.start()
    ptable = ColorTable(["Feed Source", "Transit URL", "Bounding Box"], theme=Themes.OCEAN)
    for src in feed_sources:
        feed_bbox: Bbox = src.bbox
        if predicate == "contains":
            if not bbox_contains_bbox(feed_bbox, bbox):
                continue
        elif predicate == "intersects":
            if (not bbox_intersects_bbox(feed_bbox, bbox)) and (
                not bbox_intersects_bbox(bbox, feed_bbox)
            ):
                continue

        row = [
            src.__name__,
            src.url,
            [feed_bbox.min_x, feed_bbox.min_y, feed_bbox.max_x, feed_bbox.max_y],
        ]
        ptable.add_row(row)

    print(
        "\n" + f"Feeds based on bbox input {bbox} and "
        f"for predicate={predicate.value} are as follows:"
    )
    print("\n" + ptable.get_string())
    spinner.succeed("All done!")


@app.command()
def fetch_feeds(sources=None):
    """
    :param sources: List of :FeedSource: modules to fetch; if not set, will fetch all available.
    """
    statuses = {}  # collect the statuses for all the files

    # make a copy of the list of all modules in feed_sources;
    # default to use all of them
    if not sources:
        sources = list(feed_sources.__all__)

    LOG.info("Going to fetch feeds from sources: %s", sources)
    for src in sources:
        LOG.debug("Going to start fetch for %s...", src)
        try:
            module = getattr(feed_sources, src)
            # expect a class with the same name as the module; instantiate and fetch its feeds
            klass = getattr(module, src)
            if issubclass(klass, FeedSource):
                inst = klass()
                inst.fetch()
                statuses.update(inst.status)
            else:
                LOG.warn(
                    "Skipping class %s, which does not subclass FeedSource.",
                    klass.__name__,
                )
        except AttributeError:
            LOG.error("Skipping feed %s, which could not be found.", src)

    # remove last check key set at top level of each status dictionary
    if "last_check" in statuses:
        del statuses["last_check"]

    # display results
    ptable = ColorTable()

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

    ptable.field_names = [
        "file",
        "new?",
        "valid?",
        "current?",
        "newly effective?",
        "error",
    ]
    LOG.info("Results:\n%s", ptable.get_string())
    LOG.info("All done!")


if __name__ == "__main__":
    app()
