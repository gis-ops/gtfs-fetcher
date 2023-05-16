#!/usr/bin/env python
"""Command line interface for fetching GTFS."""
import typer
from typing_extensions import Annotated
from chalky import chain
import logging
from prettytable.colortable import ColorTable, Themes
from halo import Halo
from .feed_source import FeedSource
from .feed_sources import __all__ as feed_sources

logging.basicConfig()
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)
app = typer.Typer()
            
@app.command()
def list_feeds(bbox: Annotated[str, typer.Argument(help="pass value as a string separated by commas like this: xmin,ymin,xmax,ymax ")],
    predicate: Annotated[str, typer.Option(help="intersects or contains")] = 'intersects'):
    """Filter feeds spatially based on bounding box."""
    spinner = Halo(text='Filtering...', text_color="cyan", spinner='dots')
    spinner.start()
    xmin, ymin, xmax, ymax = [float(coord) for coord in bbox.split(',')]
    ptable = ColorTable(['Feed Source', 'Transit URL', 'Bounding Box'], theme=Themes.OCEAN)
    for src in feed_sources:
        inst = src()
        feed_xmin, feed_ymin, feed_xmax, feed_ymax = inst.bbox
        if predicate == 'contains':
            if (feed_xmin >= xmin and feed_xmin < xmax) and (feed_ymin >= ymin and feed_ymin < ymax) and (feed_xmax <= xmax and feed_xmax > xmin) and (feed_ymax <= ymax and feed_ymax > ymin):
                row=[src, chain.bright_yellow | inst.url , bbox ]
                ptable.add_row(row)
        else:
            # intersects
            if (feed_xmin >= xmin and feed_xmin <= xmax) or (feed_ymin >= ymin and feed_ymin <= ymax) or (feed_xmax <= xmax and feed_xmax >= xmin) or (feed_ymax <= ymax and feed_ymax >= ymin) or (xmin >= feed_xmin and xmin <= feed_xmax) or (ymin >= feed_ymin and ymin <= feed_ymax) or (xmax <= feed_xmax and xmax >= feed_xmin) or (ymax <= feed_ymax and ymax >= feed_ymin):
                row=[src, chain.bright_yellow | inst.url , bbox ]
                ptable.add_row(row)
    print("\n" + f"Feeds based on bbox input {chain.bright_yellow | [xmin, ymin, xmax, ymax]} are as follows:")     
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

    LOG.info('Going to fetch feeds from sources: %s', sources)
    for src in sources:
        LOG.debug('Going to start fetch for %s...', src)
        try:
            module = getattr(feed_sources, src)
            # expect a class with the same name as the module; instantiate and fetch its feeds
            klass = getattr(module, src)
            if issubclass(klass, FeedSource):
                inst = klass()
                inst.fetch()
                statuses.update(inst.status)
            else:
                LOG.warn('Skipping class %s, which does not subclass FeedSource.', klass.__name__)
        except AttributeError:
            LOG.error('Skipping feed %s, which could not be found.', src)

    # remove last check key set at top level of each status dictionary
    if statuses.has_key('last_check'):
        del statuses['last_check']

    # display results
    ptable = ColorTable()

    for file_name in statuses:
        stat = statuses[file_name]
        msg = []
        msg.append(file_name)
        msg.append('x' if stat.has_key('is_new') and stat['is_new'] else '')
        msg.append('x' if stat.has_key('is_valid') and stat['is_valid'] else '')
        msg.append('x' if stat.has_key('is_current') and stat['is_current'] else '')
        msg.append('x' if stat.has_key('newly_effective') and stat.get('newly_effective') else '')
        if stat.has_key('error'):
             msg.append(stat['error'])
        else:
             msg.append('')
        ptable.add_row(msg)

    ptable.field_names = ['file', 'new?', 'valid?', 'current?', 'newly effective?', 'error']
    LOG.info('Results:\n%s', ptable.get_string())
    LOG.info('All done!')

if __name__ == '__main__':
    app()
