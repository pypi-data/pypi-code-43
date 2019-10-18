# -*- coding: utf-8 -*-
"""Graphing data from Octopus Energy API"""
from octopy_graph.query import MeterQueryTool, GasMeter, ElectricityMeter, Period
from octopy_graph.graph import (
    average_hourly_consumption,
    average_daily_consumption,
    average_weekly_consumption,
    daily_consumption,
    weekly_consumption,
)
