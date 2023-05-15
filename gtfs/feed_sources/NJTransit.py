"""Fetch NJ TRANSIT bus and rail feeds.

Requires username and password to log in first.
Cannot check for whether a feed is new or not, so only call to fetch this one once
an email is sent to the developer account saying new feeds are available.
"""
import logging
from utils.set_dict_attrs import set_dict_attrs
from utils.FeedSource import FeedSource


LOG = logging.getLogger(__name__)

URL = 'https://www.njtransit.com/'

feeds = {
    'nj_rail.zip': URL + 'rail_data.zip',
    'nj_bus.zip': URL + 'bus_data.zip'
}

class NJTransit(FeedSource):
    """Create session to fetch NJ TRANSIT feed bus and rail feeds."""
    def __init__(self):
        super(NJTransit, self).__init__()
        set_dict_attrs(self, feeds)

    def fetch(self):
        """Fetch NJ TRANSIT bus and rail feeds.

        First logs on to create session before fetching and validating downloads.
        """
        for filename in self.urls:
            url = self.urls.get(filename)
            self.fetchone(filename, url)
            self.write_status()



