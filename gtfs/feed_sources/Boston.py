"""Fetch Massacheusetts Bay Transportation Authority (Boston) feed."""
import logging
from utils.set_dict_attrs import set_dict_attrs
from utils.FeedSource import FeedSource
LOG = logging.getLogger(__name__)

feeds = {
    'boston.zip': 'http://www.mbta.com/uploadedfiles/MBTA_GTFS.zip'
}

class Boston(FeedSource):
    """Fetch MBTA feed."""
    def __init__(self):
        super(Boston, self).__init__()
        set_dict_attrs(self, feeds)
