"""Fetch Capital District Transportation Authority (Albany, New York) feed."""
from ..feed_source import FeedSource


class AlbanyNy(FeedSource):
    """Fetch CDTA feed."""

    url: str = "http://www.cdta.org/schedules/google_transit.zip"
    bbox: list[float] = [-74.219321, 42.467161, -73.614608, 43.10706]
