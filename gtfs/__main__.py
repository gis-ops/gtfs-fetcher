#!/usr/bin/env python
"""Command line interface for fetching GTFS."""
from typing import Optional

import typer
from prettytable.colortable import ColorTable, Themes
from typing_extensions import Annotated

from .feed_sources import feed_sources
from .utils.check_params import check_bbox, check_output_dir, check_sources
from .utils.constants import LOG, Predicate, spinner
from .utils.geom import Bbox, bbox_contains_bbox, bbox_intersects_bbox
from .utils.multithreading import multi_fetch

app = typer.Typer(help="Fetch GTFS feeds from various transit agencies.")


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
    search: Annotated[
        Optional[str],
        typer.Option(
            "--search",
            "-s",
            help="search for feeds based on a string",
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
    """Filter feeds spatially based on bounding box or search string.

    :param bbox: set of coordinates to filter feeds spatially
    :param predicate: the gtfs feed should intersect or should be contained inside the user's bbox
    :param search: Search for feeds based on a string.
    :param pretty: display feeds inside a pretty table
    """
    sources: list = feed_sources

    if search is not None:
        if bbox is not None or predicate is not None:
            raise typer.BadParameter(
                "Please pass either bbox or search text, not both at the same time!"
            )
        else:
            sources = [src for src in feed_sources if search.lower() in src.__name__.lower()]

    if bbox is None and predicate is not None:
        raise typer.BadParameter(
            f"Please pass a bbox if you want to filter feeds spatially based on predicate = {predicate}!"
        )

    if bbox is not None and predicate is None:
        raise typer.BadParameter(
            f"Please pass a predicate if you want to filter feeds spatially based on bbox = {bbox}!"
        )

    spinner("Filtering feeds...", 1)

    if pretty is True:
        pretty_output = ColorTable(
            ["Feed Source", "Transit URL", "Bounding Box"], theme=Themes.OCEAN, hrules=1
        )

    for src in sources:
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
    output_dir: Annotated[
        str,
        typer.Option(
            "--output-dir",
            "-o",
            help="the directory where the downloaded feeds will be saved, default is feeds",
            callback=check_output_dir,
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
    :param output_dir: The directory where the downloaded feeds will be saved; default is "feeds"
     in current working directory.
    :param concurrency: The number of concurrent downloads; default is 4.
    """

    if not sources:
        sources = feed_sources
    else:
        sources = [src for src in feed_sources if src.__name__.lower() in sources.lower()]

    LOG.info(f"Going to fetch feeds from sources: {sources}")

    multi_fetch(sources, output_dir, concurrency)


if __name__ == "__main__":
    app()
