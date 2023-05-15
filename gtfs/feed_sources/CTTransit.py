"""Fetch CT Transit (Connecticut) feeds."""
import logging
from utils.set_dict_attrs import set_dict_attrs
from utils.FeedSource import FeedSource

LOG = logging.getLogger(__name__)

feeds ={
    'ct_transit.zip': 'http://www.cttransit.com/sites/default/files/gtfs/googlect_transit.zip',
    'ct_shoreline_east.zip': 'http://www.shorelineeast.com/google_transit.zip',
    'ct_hartford_rail.zip': 'http://www.hartfordline.com/files/gtfs/gtfs.zip'
}

class CTTransit(FeedSource):
    """Fetch CT Transit (Connecticut) feed."""
    def __init__(self):
        super(CTTransit, self).__init__()
        set_dict_attrs(self, feeds)

