"""Defines base class for feed(s) from an agency.

To add a new feed, add a subclass of this to the `feed_sources` directory.
"""
import logging
from abc import ABC, abstractmethod, abstractproperty

class FeedSource(ABC):
    """Base class for a GTFS source. Class and module names are expected to match.

    Subclass this class and:
        - set :url: is the URL where the feed will be downloaded from
              :bbox: bbox for the gtfs feed based on 'stops' dataset
        - override :fetch: method as necessary to fetch feeds for the agency.
    """

    @abstractproperty
    def url(self):
        pass
    
    @abstractproperty
    def bbox(self):
        pass

    def fetch(self):
        pass
