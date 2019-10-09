from __future__ import print_function

from elasticsearchlib.elasticsearchlib import Elasticsearchlib

def test_true():
    assert True
#def test_start_connection():
#    # TODO Change ip:port to environment variable
#    eslib = Elasticsearchlib()
#    conn = eslib.start_connection("95.211.12.18", "9200")
#    is_connected = conn.ping()
#    assert is_connected

#def test_start_connection_fail():
#    # TODO Change ip:port to environment variable
#    eslib = Elasticsearchlib()
#    conn = eslib.start_connection("95.211.12.1", "9200")
#    is_connected = conn.ping()
#    assert not is_connected
