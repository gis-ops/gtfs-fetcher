"""Fetch Berlin feed."""
from utils.FeedSource import FeedSource

class Berlin(FeedSource):
    """Fetch Berlin feed."""
    def __init__(self):
        super(Berlin, self).__init__()
        self.url: str = 'https://www.vbb.de/fileadmin/user_upload/VBB/Dokumente/API-Datensaetze/gtfs-mastscharf/GTFS.zip'
        self.bbox: list[float] = [10.669821, 50.839245, 17.037088, 54.308626]
