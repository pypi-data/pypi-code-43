#!/usr/bin/env python3

"""
API - fetch data from the public President's Cup Leaderboards
"""

import json
import datetime
import logging
import urllib.request

COMP_HOURS = 8

def event_to_url(e):
    return "{}/api/leaderboard/{}?sort=rank&take={}".format(e["url"], e["event_id"], e["take"])

def fetch_event(event):
    """Fetch publicly accesible json scoreboard data"""
    url = event_to_url(event)
    with urllib.request.urlopen(url) as resp:
       j = resp.read()
       return json.loads(j)
    
def parse_time(timestamp):
    """Takes a timestamp string from the API and returns a datetime object
    e.g. "2019-10-07T13:10:01.08837Z" or "2019-10-18T14:03:00Z"
    """
    try:
        t = datetime.datetime.strptime(timestamp,"%Y-%m-%dT%H:%M:%S.%fZ")
        return t
    # sometimes the API returns a different format
    except ValueError:
        logging.debug("Time failed to parse: {}".format(timestamp))
        t = datetime.datetime.strptime(timestamp,"%Y-%m-%dT%H:%M:%SZ") 
    return t

#def api_time_to_local(timestamp):
#    t = parse_time(timestamp)
#    return t.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)


def start_to_time_left(s, cur):
    """Compute useable time strings"""
    start = parse_time(s)
    diff = cur-start
    active = diff < datetime.timedelta(hours=COMP_HOURS)
    delta = datetime.timedelta(hours=COMP_HOURS) - diff
    if active:
        left = (datetime.datetime.utcfromtimestamp(0) + delta).strftime('%H:%M:%S')
    else:
        left = "Final"
    return left, active
