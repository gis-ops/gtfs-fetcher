"""Fetch Capital District Transportation Authority (Albany, New York) feed."""
import logging
from utils.set_dict_attrs import set_dict_attrs

from utils.FeedSource import FeedSource

feeds = {
    'albany_ny.zip': 'http://www.cdta.org/schedules/google_transit.zip'
}

LOG = logging.getLogger(__name__)

class AlbanyNy(FeedSource):
    """Fetch CDTA feed."""
    def __init__(self):
        super(AlbanyNy, self).__init__()
        set_dict_attrs(self, feeds)
