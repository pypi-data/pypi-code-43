# -*- coding: utf-8 -*-
"""Drummer events.

This module provides all service-side events

An event is an action triggered by a command issued by the user.
"""
from .sockets import SocketTestEvent
from .jobs import JobAddEvent, JobRemoveEvent
from .jobs import JobDisableEvent, JobEnableEvent
from .jobs import JobListEvent, JobGetEvent, JobExecEvent
