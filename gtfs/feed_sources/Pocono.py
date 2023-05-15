"""Fetch Monroe Country Transit Authority (Pocono Pony) feed.

Looks like GTFSExchange is the authoritative source for this feed.
"""
import logging
from utils.set_dict_attrs import set_dict_attrs
from utils.FeedSource import FeedSource

LOG = logging.getLogger(__name__)

feeds = {
    'pocono.zip': 'http://www.gtfs-data-exchange.com/agency/monroe-county-transit-authority/latest.zip'
}

class Pocono(FeedSource):
    """Fetch Monroe County feed."""
    def __init__(self):
        super(Pocono, self).__init__()
        set_dict_attrs(self, feeds)
