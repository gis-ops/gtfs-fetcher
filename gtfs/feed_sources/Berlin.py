"""Fetch Berlin feed."""
from ..feed_source import FeedSource

class Berlin(FeedSource):
    """Fetch Berlin feed."""
    url: str = 'https://www.vbb.de/fileadmin/user_upload/VBB/Dokumente/API-Datensaetze/gtfs-mastscharf/GTFS.zip'
    bbox: list[float] = [10.669821, 50.839245, 17.037088, 54.308626]
