from libra.ledger_info import *
import libra
from datetime import datetime
import time
import pytest
import pdb

def time_offset_in_hours():
    return time.localtime().tm_hour - time.gmtime().tm_hour

def time_offset_in_seconds():
    return -time.timezone

def test_time():
    assert time_offset_in_hours()*3600 == time_offset_in_seconds()
    utcnow = datetime.utcnow().timestamp()
    now = datetime.now().timestamp()
    diff = (now - time_offset_in_seconds()) - utcnow
    assert diff > 0
    assert diff < 1

def test_ledger_info():
    c = libra.Client("testnet")
    info = c.get_latest_ledger_info()
    assert info.version > 0
    assert len(info.transaction_accumulator_hash) == 32
    assert len(info.consensus_data_hash) == 32
    assert len(info.consensus_block_id) == 32
    assert info.timestamp_usecs > 1570_000_000_000_000
    secs = info.timestamp_usecs / 1000_000
    assert abs(datetime.now().timestamp() - secs) < 5
    #assert abs(datetime.utcnow().timestamp() - secs) < 5

