"""Fetch Delaware First State feed."""
import logging
from utils.set_dict_attrs import set_dict_attrs
from utils.FeedSource import FeedSource

LOG = logging.getLogger(__name__)

feeds = {
    'delaware.zip': 'https://dartfirststate.com/RiderInfo/Routes/gtfs_data/dartfirststate_de_us.zip'
}

class Delaware(FeedSource):
    """Fetch DART feed."""
    def __init__(self):
        super(Delaware, self).__init__()
        set_dict_attrs(self, feeds)
