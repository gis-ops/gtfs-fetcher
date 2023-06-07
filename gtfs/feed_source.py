"""Defines base class for feed(s) from an agency.

To add a new feed, add a subclass of this to the `feed_sources` directory.
"""
import os
import pickle

# import subprocess
import zipfile
from abc import ABC, abstractmethod
from datetime import datetime

import requests

from gtfs.utils.constants import LOG
from gtfs.utils.geom import Bbox

# format time checks like last-modified header
TIMECHECK_FMT = "%a, %d %b %Y %H:%M:%S GMT"


class FeedSource(ABC):
    """Base class for a GTFS source. Class and module names are expected to match.

    Subclass this class and:
        - set :url: is the URL where the feed will be downloaded from
              :bbox: bbox for the gtfs feed based on 'stops' dataset
        - override :fetch: method as necessary to fetch feeds for the agency.
    """

    def __init__(self):
        self.status = {}
        self.ddir = ""
        self.status_file = ""

    @property
    @abstractmethod
    def url(self) -> str:
        pass

    @property
    @abstractmethod
    def bbox(self) -> Bbox:
        pass

    def write_status(self):
        """Write pickled log of feed statuses and last times files were downloaded."""
        LOG.debug(f"Downloading finished. Writing status file {self.status_file}...")
        with open(self.status_file, "wb") as status_file:
            pickle.dump(self.status, status_file)
            LOG.debug(f"Statuses written to {self.status_file}.")

    # TODO - add a method to verify the feed
    def fetch(self) -> bool:
        """Modify this method in subclass for importing feed(s) from agency.

        By default, checks the last-modified header to see if a new
        download is available, streams the download if so, and verifies the new GTFS.
        """
        if self.url:
            feed_file = self.__class__.__name__
            if self.download_feed(feed_file, self.url):
                self.write_status()
                # if self.verify(feed_file):
                #     LOG.info('GTFS verification succeeded.')
                #     return True
                # else:
                #     LOG.error('GTFS verification failed.')
                #     return False
            else:
                return False
        else:
            raise ValueError("URL not set for feed source!")

    def check_header_newer(self, feed_file: str, url: str):
        """Check if last-modified header indicates a new download is available.

        :param feed_file: Name of downloaded file (relative to :ddir:)
        :param url: Where GTFS is downloaded from
        :returns: 1 if newer GTFS available; 0 if info missing; -1 if already have most recent
        """
        if not os.path.exists(self.status_file):
            LOG.debug(f"Status file {self.status_file} not found.")
            return 0

        with open(self.status_file, "rb") as f:
            last_status = pickle.load(f)
        if feed_file in last_status and "posted_date" in last_status[feed_file]:
            last_fetch = last_status[feed_file]["posted_date"]
            hdr = requests.head(url)
            hdr = hdr.headers
            if hdr.get("last-modified"):
                last_mod = hdr.get("last-modified")
                if last_fetch >= last_mod:
                    LOG.info(f"No new download available for {feed_file}.")
                    return -1
                else:
                    LOG.info(f"New download available for {feed_file}.")
                    LOG.info(f"Last download from: {last_fetch}.")
                    LOG.info(f"New download posted: {last_mod}")
                    return 1
            else:
                # should try to find another way to check for new feeds if header not set
                LOG.debug(f"No last-modified header set for {feed_file} download link.")
                return 0
        else:
            LOG.debug(f"Time check entry for {feed_file} not found.")
            return 0

    def download_feed(self, feed_file: str, url: str, do_stream: bool = True) -> bool:
        """Download feed.

        :param feed_file: File name to save download as, relative to :ddir:
        :param url: Where to download the GTFS from
        :param do_stream: If True, stream the download
                :returns: True if download was successful
        """
        if self.check_header_newer(feed_file, url) == -1:
            # Nothing new to fetch; done here
            return False

        # feed_file is local to download directory
        feed_file_path = os.path.join(self.ddir, feed_file + ".zip")
        LOG.info(f"Getting file {feed_file}...from...{url}")
        request = requests.get(url, stream=do_stream)

        if request.ok:
            with open(feed_file_path, "wb") as download_file:
                if do_stream:
                    for chunk in request.iter_content(chunk_size=1024):
                        download_file.write(chunk)
                else:
                    download_file.write(request.content)

            info = os.stat(feed_file_path)
            if info.st_size < 10000:
                # file smaller than 10K; may not be a GTFS
                LOG.warning(f"Download for {feed_file_path} is only {str(info.st_size)} bytes.")
            if not zipfile.is_zipfile(feed_file_path):
                self.set_error(feed_file, "Download is not a zip file")
                return False
            posted_date = request.headers.get("last-modified")
            if not posted_date:
                LOG.debug("No last-modified header set")
                posted_date = datetime.utcnow().strftime(TIMECHECK_FMT)
            self.set_posted_date(feed_file, posted_date)
            LOG.info("Download completed successfully.")
            return True
        else:
            self.set_error(feed_file, "Download failed")
            return False

    def set_posted_date(self, feed_file: str, posted_date: str):
        """Update feed status posted date. Creates new feed status if none found.

        :param feed_file: Name of feed file, relative to :ddir:
        :param posted_date: Date string formatted to :TIMECHECK_FMT: when feed was posted
        """
        stat = self.status.get(feed_file, {})
        stat["posted_date"] = posted_date
        self.status[feed_file] = stat

    def set_error(self, feed_file: str, msg: str):
        """If error encountered in processing, set status error message, and unset other fields.

        :param feed_file: Name of feed file, relative to :ddir:
        :param msg: Error message to save with status
        """
        LOG.error(f"Error processing {feed_file}: {msg}")
        self.status[feed_file] = {"error": msg}
        self.write_status()
