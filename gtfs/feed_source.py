"""Defines base class for feed(s) from an agency.

To add a new feed, add a subclass of this to the `feed_sources` directory.
"""
from abc import ABC, abstractmethod

from gtfs.utils.geom import Bbox


class FeedSource(ABC):
    """Base class for a GTFS source. Class and module names are expected to match.

    Subclass this class and:
        - set :url: is the URL where the feed will be downloaded from
              :bbox: bbox for the gtfs feed based on 'stops' dataset
        - override :fetch: method as necessary to fetch feeds for the agency.
    """

    @property
    @abstractmethod
    def url(self) -> str:
        pass

    @property
    @abstractmethod
    def bbox(self) -> Bbox:
        pass

    def fetch(self):
        """
        Modify this method in subclass for importing feed(s) from agency.

        By default, loops over given URLs, checks the last-modified header to see if a new
        download is available, streams the download if so, and verifies the new GTFS.
        """
