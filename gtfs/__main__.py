#!/usr/bin/env python
"""Command line interface for fetching GTFS."""
import os
import threading
from typing import Optional

import typer
from prettytable.colortable import ColorTable, Themes
from typing_extensions import Annotated

from .feed_source import FeedSource
from .feed_sources import feed_sources
from .utils.constants import LOG, Predicate, spinner
from .utils.geom import Bbox, bbox_contains_bbox, bbox_intersects_bbox

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


def check_sources(sources: str) -> Optional[str]:
    """Check if the sources are valid."""
    if sources is None:
        return None
    sources = sources.split(",")
    for source in sources:
        if not any(src.__name__.lower() == source.lower() for src in feed_sources):
            raise typer.BadParameter(f"{source} is not a valid feed source!")

    return ",".join(sources)


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
    """Filter feeds spatially based on bounding box or list all of them.

    :param bbox: set of coordinates to filter feeds spatially
    :param predicate: the gtfs feed should intersect or should be contained inside the user's bbox
    :param pretty: display feeds inside a pretty table
    """
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

        filtered_srcs = ""

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

            filtered_srcs += src.__name__ + ", "

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

        if typer.confirm("Do you want to fetch feeds from these sources?"):
            fetch_feeds(sources=filtered_srcs[:-1])


@app.command()
def fetch_feeds(
    sources: Annotated[
        Optional[str],
        typer.Option(
            "--sources",
            "-src",
            help="pass value as a string separated by commas like this: Berlin,AlbanyNy,...",
            callback=check_sources,
        ),
    ] = None,
    search: Annotated[
        Optional[str],
        typer.Option(
            "--search",
            "-s",
            help="search for feeds based on a string",
        ),
    ] = None,
    output_dir: Annotated[
        Optional[str],
        typer.Option(
            "--output-dir",
            "-o",
            help="the directory where the downloaded feeds will be saved, default is feeds",
        ),
    ] = "feeds",
    concurrency: Annotated[
        Optional[int],
        typer.Option(
            "--concurrency",
            "-c",
            help="the number of concurrent downloads, default is 4",
        ),
    ] = 4,
) -> None:
    """Fetch feeds from sources.

    :param sources: List of :FeedSource: modules to fetch; if not set, will fetch all available.
    :param search: Search for feeds based on a string.
    :param output_dir: The directory where the downloaded feeds will be saved; default is feeds.
    :param concurrency: The number of concurrent downloads; default is 4.
    """
    # statuses = {}  # collect the statuses for all the files

    if not sources:
        if not search:
            # fetch all feeds
            sources = feed_sources
        else:
            # fetch feeds based on search
            sources = [
                src
                for src in feed_sources
                if search.lower() in src.__name__.lower() or search.lower() in src.url.lower()
            ]
    else:
        if search:
            raise typer.BadParameter("Please pass either sources or search, not both at the same time!")
        else:
            sources = [src for src in feed_sources if src.__name__.lower() in sources.lower()]

    output_dir_path = os.path.join(os.getcwd(), output_dir)
    if not os.path.exists(output_dir_path):
        os.makedirs(output_dir_path)

    LOG.info(f"Going to fetch feeds from sources: {sources}")

    threads = []

    def thread_worker():
        while True:
            try:
                src = sources.pop(0)
            except IndexError:
                break

            LOG.debug(f"Going to start fetch for {src}...")
            try:
                if issubclass(src, FeedSource):
                    inst = src()
                    inst.ddir = output_dir_path
                    inst.status_file = os.path.join(inst.ddir, src.__name__ + ".pkl")
                    inst.fetch()
                    # statuses.update(inst.status)
                else:
                    LOG.warning(f"Skipping class {src.__name__}, which does not subclass FeedSource.")
            except AttributeError:
                LOG.error(f"Skipping feed {src}, which could not be found.")

    for _ in range(concurrency):
        thread = threading.Thread(target=thread_worker)
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # ptable = ColorTable(
    #     [
    #         "file",
    #         "new?",
    #         "valid?",
    #         "current?",
    #         "newly effective?",
    #         "error",
    #     ],
    #     theme=Themes.OCEAN,
    #     hrules=1,
    # )
    #
    # for file_name in statuses:
    #     stat = statuses[file_name]
    #     msg = []
    #     msg.append(file_name)
    #     msg.append("x" if "is_new" in stat and stat["is_new"] else "")
    #     msg.append("x" if "is_valid" in stat and stat["is_valid"] else "")
    #     msg.append("x" if "is_current" in stat and stat["is_current"] else "")
    #     msg.append("x" if "newly_effective" in stat and stat.get("newly_effective") else "")
    #     if "error" in stat:
    #         msg.append(stat["error"])
    #     else:
    #         msg.append("")
    #     ptable.add_row(msg)
    #
    # LOG.info("\n" + ptable.get_string())


if __name__ == "__main__":
    app()
