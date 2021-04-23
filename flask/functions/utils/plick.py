import requests
import logging

def get_ads(query, limit = 5):
    r = requests.get("https://api.plick.se/api/v3/ads?query={}&limit={}".format(query,limit))
    if (r.status_code == 200):
        return r.json()
    else:
        return r.status_code