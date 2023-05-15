#!/usr/bin/env python
"""Command line interface for fetching GTFS."""
import typer
from chalky import chain
import logging
from prettytable import PrettyTable
from halo import Halo
import importlib
from utils.FeedSource import FeedSource
import feed_sources

logging.basicConfig()
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)
app = typer.Typer()
sources = list(feed_sources.__all__)
            
@app.command()
def list_feeds(xmin:float, ymin:float, xmax:float, ymax:float):
    """Filter feeds spatially based on bounding box. Pass negative args as ' -45.6774' for example."""
    spinner = Halo(text='Filtering...', text_color="cyan", spinner='dots')
    spinner.start()
    ptable = PrettyTable(['Transit URL', 'Bounding Box'])
    
    for src in sources:
        module = importlib.import_module('feed_sources.' + src)
        klass = getattr(module, src)
        inst = klass()
        bbox = inst.bbox
        if (bbox[0] >= xmin and bbox[0] < xmax) and (bbox[1] >= ymin and bbox[1] < ymax) and (bbox[2] <= xmax and bbox[2] > xmin) and (bbox[3] <= ymax and bbox[3] > ymin):
            row=[ chain.bright_yellow | inst.url , bbox ]
            ptable.add_row(row)
    print(f"\n Feeds based on bbox input {chain.bright_yellow | [xmin, ymin, xmax, ymax]} are as follows:")     
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
    ptable = PrettyTable()

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
