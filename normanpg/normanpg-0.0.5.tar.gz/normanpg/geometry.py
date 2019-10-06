#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created on 9/22/19 by pat
"""
.. currentmodule:: normanpg.geometry
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This module contains conveniences for working with geometries.
"""
from shapely.geometry.base import BaseGeometry
from shapely import wkb


def shape(obj: str) -> BaseGeometry:
    """
    Convert a geometry from Postgres into a
    `Shapely <https://shapely.readthedocs.io/en/stable/manual.html#geometric-objects>`_
    geometry.

    :param obj: the raw geometry retrieved from Postgres (a WKB hex string)
    :return: the `Shapely` geometry
    """
    return wkb.loads(obj, hex=True)
