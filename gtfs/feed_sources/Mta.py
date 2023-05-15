"""Fetch MTA (New York City) feeds."""
import logging
from utils.set_dict_attrs import set_dict_attrs
from utils.FeedSource import FeedSource

BASE_URL = 'http://web.mta.info/developers/data/'

LOG = logging.getLogger(__name__)

feeds = {
    'nyc_sub_url': '%snyct/subway/google_transit.zip' % BASE_URL,
    'bronx_bus_url': '%snyct/bus/google_transit_bronx.zip' % BASE_URL,
    'brooklyn_bus_url': '%snyct/bus/google_transit_brooklyn.zip' % BASE_URL,
    'manhattan_bus_url': '%snyct/bus/google_transit_manhattan.zip' % BASE_URL,
    'queens_bus_url': '%snyct/bus/google_transit_queens.zip' % BASE_URL,
    'staten_bus_url': '%snyct/bus/google_transit_staten_island.zip' % BASE_URL,
    'lirr_url': '%slirr/google_transit.zip' % BASE_URL,
    'metro_north_url': '%smnr/google_transit.zip' % BASE_URL,
    'busco_url': '%sbusco/google_transit.zip' % BASE_URL
}

class Mta(FeedSource):
    """Fetch MTA (NYC) feeds."""
    def __init__(self):
        super(Mta, self).__init__()
        set_dict_attrs(self, feeds)


    def fetch(self):
        """MTA downloads do not stream."""
        for filename in self.urls:
            self.fetchone(filename, self.urls.get(filename), do_stream=False)
            self.write_status()
