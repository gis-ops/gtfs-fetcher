from io import BytesIO
from zipfile36 import ZipFile
import requests
import pandas as pd
import logging
from chalky import chain
LOG = logging.getLogger()

def get_bbox(url: str):
    try:
        zip = ZipFile(BytesIO(requests.get(url).content))
        df_dict = pd.read_csv(zip.open('stops.txt'))
        return [df_dict['stop_lon'].min(), df_dict['stop_lat'].min(), df_dict['stop_lon'].max(), df_dict['stop_lat'].max()]
    except:
        LOG.error('Failed to get bbox attr for %s', chain.bright_red | url)
        return None

def set_dict_attrs(self: object, feeds: dict):
    self.urls = {}
    for feed in feeds:
        self.urls[feed] = {"url": feeds[feed], "bbox": None}