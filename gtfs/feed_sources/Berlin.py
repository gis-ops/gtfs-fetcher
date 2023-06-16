"""Fetch Berlin feed."""
from ..feed_source import FeedSource
from ..utils.geom import Bbox


class Berlin(FeedSource):
    """Fetch Berlin feed."""

    url: str = (
        "https://www.vbb.de/fileadmin/user_upload/VBB/Dokumente/API-Datensaetze/gtfs-mastscharf/GTFS.zip"
    )
    bbox: Bbox = Bbox(10.669821, 50.839245, 17.037088, 54.308626)

    def __init__(self):
        super().__init__()
