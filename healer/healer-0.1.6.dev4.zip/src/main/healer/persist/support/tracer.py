"""
Sqlite performance profiler
"""

from __future__ import annotations

from typing import Any

import apsw


class TracerReactor():
    ""

    def react(self, cursor:Any, statement:str, bindings:list):
        pass


class StoredTracer():

    conn:apsw.Connection
    reactor:TracerReactor

    def __init__(self, conn:apsw.Connection, reactor:TracerReactor):
        self.conn = conn
        self.reactor = reactor

    def enable(self):
        self.conn.setexectrace(self.reactor)

    def disable(self):
        self.conn.setexectrace(None)
