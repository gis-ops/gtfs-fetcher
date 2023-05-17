#!/usr/bin/env python
"""Command line interface for fetching GTFS."""
import logging

import typer
from chalky import chain
from halo import Halo
from prettytable.colortable import ColorTable, Themes
from typing_extensions import Annotated

from .feed_source import FeedSource
from .feed_sources import __all__ as feed_sources
from .utils.constants import Predicate
from .utils.geom import bbox_contains_bbox, bbox_intersects_bbox

logging.basicConfig()
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)
app = typer.Typer()


def check_bbox(bbox: str):
    if "," not in bbox or len(bbox.split(",")) != 4:
        raise typer.BadParameter(
            chain.bright_red
            | "Please pass bbox as a string separated by commas like this: xmin,ymin,xmax,ymax"
        )
    for coord in bbox.split(","):
        try:
            float(coord)
        except ValueError:
            raise typer.BadParameter(chain.bright_red | "Please pass only numbers as bbox values!")
    return bbox


@app.command()
def list_feeds(
    bbox: Annotated[
        str,
        typer.Argument(
            help="pass value as a string separated by commas like this: xmin,ymin,xmax,ymax ",
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
):
    """Filter feeds spatially based on bounding box."""
    spinner = Halo(text="Filtering...", text_color="cyan", spinner="dots")
    spinner.start()
    user_bbox = [float(coord) for coord in bbox.split(",")]
    ptable = ColorTable(["Feed Source", "Transit URL", "Bounding Box"], theme=Themes.OCEAN)
    for src in feed_sources:
        feed_bbox = src.bbox
        if predicate == "contains":
            if bbox_contains_bbox(feed_bbox, user_bbox):
                row = [src, chain.bright_yellow | src.url, feed_bbox]
                ptable.add_row(row)
        else:
            if bbox_intersects_bbox(feed_bbox, user_bbox):
                row = [src, chain.bright_yellow | src.url, feed_bbox]
                ptable.add_row(row)
    print(
        "\n"
        + f"Feeds based on bbox input {chain.bright_yellow | user_bbox} and \
            for predicate={chain.bright_yellow | predicate.value} are as follows:"
    )
    print("\n" + ptable.get_string())
    spinner.succeed(chain.bright_green.bold | "All done!")


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
