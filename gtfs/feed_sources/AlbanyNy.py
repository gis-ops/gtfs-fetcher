"""Fetch Capital District Transportation Authority (Albany, New York) feed."""
from utils.FeedSource import FeedSource

class AlbanyNy(FeedSource):
    """Fetch CDTA feed."""
    def __init__(self):
        super(AlbanyNy, self).__init__()
        self.url: str = 'http://www.cdta.org/schedules/google_transit.zip'
        self.bbox: list[float] = [-74.219321, 42.467161, -73.614608, 43.10706]
