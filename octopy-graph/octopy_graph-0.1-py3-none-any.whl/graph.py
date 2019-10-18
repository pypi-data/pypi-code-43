# -*- coding: utf-8 -*-
"""Graphs of consumption data from the Octopus Energy API"""
from statistics import mean
from datetime import time
import numpy
import plotly.graph_objects as go

from octopy_graph.query import Period

DAYS = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}


def axis(consumptions):
    """Separate a query result into x and y axis

    >>> from collections import namedtuple
    >>> C = namedtuple("C", "interval_start consumption")
    >>> axis([C("a", 1), C("b", 2), C("c", 3)])
    (['c', 'b', 'a'], [3, 2, 1])
    >>> axis([])
    ([], [])

    :param consumptions: a list of Consumption objects
    :return: Tuple (x-axis, y-axis)
    """
    xaxis = [c.interval_start for c in reversed(consumptions)]
    yaxis = [c.consumption for c in reversed(consumptions)]
    return xaxis, yaxis


def axis_weekly_consumption(consumptions):
    """Separate a query result into x and y axis, summed per week

    >>> from collections import namedtuple
    >>> from datetime import date
    >>> C = namedtuple("C", "interval_start consumption")
    >>> axis_weekly_consumption([C(date(2017, 5, 12), 3)])
    (['[17] W19'], [3])
    >>> axis_weekly_consumption([C(date(2017, 5, 12), 3), C(date(2017, 5, 13), 2)])
    (['[17] W19'], [5])
    >>> axis_weekly_consumption([C(date(2017, 5, 12), 3), C(date(2017, 5, 15), 2)])
    (['[17] W19', '[17] W20'], [3, 2])

    :param consumptions: a list of Consumption objects
    :return: Tuple (x-axis, y-axis)
    """
    all_weeks = list({_week_num(c.interval_start) for c in consumptions})
    all_weeks = sorted(all_weeks)
    yaxis = [
        sum(c.consumption for c in consumptions if _week_num(c.interval_start) == week)
        for week in all_weeks
    ]
    return all_weeks, yaxis


def axis_average_day(consumptions):
    """Separate a query result into x and y axis, averaged per day of the week

    >>> from collections import namedtuple
    >>> from datetime import date
    >>> C = namedtuple("C", "interval_start consumption")
    >>> axis_average_day([C(date(2017, 5, 12), 3)])
    ([5], [3])
    >>> axis_average_day([C(date(2017, 5, 12), 3), C(date(2017, 5, 19), 5)])
    ([5], [4])
    >>> axis_average_day([C(date(2017, 5, 12), 3), C(date(2017, 5, 15), 4)])
    ([1, 5], [4, 3])

    :param consumptions: a list of Consumption objects
    :return: Tuple (x-axis, y-axis)
    """
    all_days = list({c.interval_start.isoweekday() for c in consumptions})
    all_days = sorted(all_days)
    yaxis = [
        mean(
            c.consumption for c in consumptions if c.interval_start.isoweekday() == day
        )
        for day in all_days
    ]
    return all_days, yaxis


def axis_average_hour(consumptions):
    """Separate a query result into x and y axis, averaged per hour

    >>> from collections import namedtuple
    >>> from datetime import time
    >>> C = namedtuple("C", "interval_start consumption")
    >>> axis_average_hour([C(time(12, 10, 20), 3)])
    ([12], [3])
    >>> axis_average_hour([C(time(12, 10, 20), 3), C(time(12, 49, 59), 7)])
    ([12], [5])
    >>> axis_average_hour([C(time(12, 00, 00), 3), C(time(11, 59, 59), 4)])
    ([11, 12], [4, 3])

    :param consumptions: a list of Consumption objects
    :return: Tuple (x-axis, y-axis)
    """
    all_hours = list({c.interval_start.hour for c in consumptions})
    all_hours = sorted(all_hours)
    yaxis = [
        mean(c.consumption for c in consumptions if c.interval_start.hour == hour)
        for hour in all_hours
    ]
    return all_hours, yaxis


def average_hourly_consumption(meter_tool):
    """Bar chart showing average hourly consumption

    :param meter_tool: a MeterQueryTool
    """
    elec_hour = meter_tool.electricity_consumption(period=Period.HOUR)
    hours, electricity = axis_average_hour(elec_hour)
    gas_hour = meter_tool.gas_consumption(period=Period.HOUR)
    _, gas = axis_average_hour(gas_hour)
    time_axis = numpy.array([time(hour=h).strftime("%H:%M") for h in hours])

    fig = go.Figure(
        data=[
            go.Bar(name="Electricity", x=time_axis, y=electricity),
            go.Bar(name="Gas", x=time_axis, y=gas),
        ]
    )

    fig.update_layout(
        barmode="group",
        title=go.layout.Title(text="Average Hourly Consumption", xref="paper", x=0),
        legend=dict(x=0.6, y=1.15),
        legend_orientation="h",
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(
                text="kWh",
                font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"),
            )
        ),
    )

    return fig


def average_daily_consumption(meter_tool):
    """Bar chart showing average consumption per day of the week

    :param meter_tool: a MeterQueryTool
    """
    elec_hour = meter_tool.electricity_consumption(period=Period.DAY)
    days, electricity = axis_average_day(elec_hour)
    gas_hour = meter_tool.gas_consumption(period=Period.DAY)
    _, gas = axis_average_day(gas_hour)
    time_axis = numpy.array([DAYS[d] for d in days])

    fig = go.Figure(
        data=[
            go.Bar(name="Electricity", x=time_axis, y=electricity),
            go.Bar(name="Gas", x=time_axis, y=gas),
        ]
    )

    fig.update_layout(
        barmode="group",
        title=go.layout.Title(text="Average Daily Consumption", xref="paper", x=0),
        legend=dict(x=0.6, y=1.15),
        legend_orientation="h",
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(
                text="kWh",
                font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"),
            )
        ),
    )

    return fig


def daily_consumption(meter_tool, date):
    """Bar chart showing consumption on a specific day

    :param meter_tool: a MeterQueryTool
    :param date: A datetime representing the date to graph
    """
    date_name = date.strftime("%d/%m/%Y")
    elec_hour = meter_tool.electricity_consumption()
    times, electricity = axis(
        [c for c in elec_hour if c.interval_start.date() == date.date()]
    )
    gas_hour = meter_tool.gas_consumption()
    _, gas = axis([c for c in gas_hour if c.interval_start.date() == date.date()])
    time_axis = numpy.array([t.strftime("%H:%M") for t in times])

    fig = go.Figure(
        data=[
            go.Bar(name="Electricity", x=time_axis, y=electricity),
            go.Bar(name="Gas", x=time_axis, y=gas),
        ]
    )

    fig.update_layout(
        barmode="group",
        title=go.layout.Title(text=f"Consumption on {date_name}", xref="paper", x=0),
        legend=dict(x=0.6, y=1.15),
        legend_orientation="h",
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(
                text="kWh",
                font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"),
            )
        ),
    )

    return fig


def weekly_consumption(meter_tool, date):
    """Bar chart showing consumption on a week day

    :param meter_tool: a MeterQueryTool
    :param date: A datetime for a date in the desired week
    """
    week_name = f"Week {date.isocalendar()[1]} {date.year}"
    elec_hour = meter_tool.electricity_consumption(period=Period.DAY)
    days, electricity = axis(
        [c for c in elec_hour if _week_num(c.interval_start) == _week_num(date)]
    )
    gas_hour = meter_tool.gas_consumption(period=Period.DAY)
    _, gas = axis(
        [c for c in gas_hour if _week_num(c.interval_start) == _week_num(date)]
    )
    time_axis = numpy.array([DAYS[d.isoweekday()] for d in days])

    fig = go.Figure(
        data=[
            go.Bar(name="Electricity", x=time_axis, y=electricity),
            go.Bar(name="Gas", x=time_axis, y=gas),
        ]
    )

    fig.update_layout(
        barmode="group",
        title=go.layout.Title(text=f"Consumption on {week_name}", xref="paper", x=0),
        legend=dict(x=0.6, y=1.15),
        legend_orientation="h",
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(
                text="kWh",
                font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"),
            )
        ),
    )

    return fig


def average_weekly_consumption(meter_tool):
    """Bar chart showing weekly consumption

    :param meter_tool: a MeterQueryTool
    """
    elec_hour = meter_tool.electricity_consumption(period=Period.WEEK)
    weeks, electricity = axis_weekly_consumption(elec_hour)
    gas_hour = meter_tool.gas_consumption(period=Period.WEEK)
    _, gas = axis_weekly_consumption(gas_hour)
    time_axis = numpy.array(weeks)

    fig = go.Figure(
        data=[
            go.Bar(name="Electricity", x=time_axis, y=electricity),
            go.Bar(name="Gas", x=time_axis, y=gas),
        ]
    )

    fig.update_layout(
        barmode="group",
        title=go.layout.Title(text="Weekly Consumption", xref="paper", x=0),
        legend=dict(x=0.6, y=1.15),
        legend_orientation="h",
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(
                text="kWh",
                font=dict(family="Courier New, monospace", size=18, color="#7f7f7f"),
            )
        ),
    )

    return fig


def _week_num(date):
    """Return the week number for a specific date

    >>> from datetime import date
    >>> _week_num(date(2018, 10, 10,))
    '[18] W41'
    >>> _week_num(date(2019, 1, 31,))
    '[19] W5'

    :param date: a datetime object
    """
    week_num = date.isocalendar()[1]
    year = date.year - 2000
    return f"[{year}] W{week_num}"
