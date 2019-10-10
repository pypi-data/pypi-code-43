""" This module wraps the Conductor API. """

CONDUCTOR_LIBRARY_VERSION = '1.6.0a4'

PRODUCTION = 'conductor.link-labs'
DEVELOP = 'dev.link-labs'
HOSPITALITY = 'hospitality.airfinder'
UAT = 'hospitality-uat.airfinder'

INSTANCES = [PRODUCTION, DEVELOP, HOSPITALITY, UAT]

import conductor
from conductor.account import ConductorAccount
from conductor.asset_group import AssetGroup
from conductor.devices.gateway import Gateway
from conductor.devices.module import Module
from conductor.event_count import EventCount
from conductor.subject import ConductorSubject, UplinkSubject, DownlinkSubject
#TODO: from conductor.subscription
from conductor.tokens import AppToken, NetToken
#TODO: conductor.util


#  TODO: delete these.
"""
import logging
LOG = logging.getLogger(__name__)

import sys
import threading
import json
import zmq
import asyncio
import websockets


from time import sleep
from datetime import datetime, timedelta
from collections import namedtuple
from operator import itemgetter
from copy import deepcopy
from enum import IntEnum

try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty
"""

