import requests
import logging


def get_ads(query, limit = 5):
    r = requests.get("http://development.plick.se/api/v3/ads?query={}&limit={}".format(query,limit))
    if (r.status_code == 200):
        logging.debug(r.json())
        return r.json()['blocks']['data']
    else:
        return r.status_code