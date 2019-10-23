#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum


class UsdaUriActions(Enum):
    """USDA API available actions"""

    list = "list"
    """Paginated lists of items"""

    report = "reports"
    """Food Reports version 1"""

    v2report = "V2/reports"
    """Food Reports version 2"""

    nutrients = "nutrients"
    """Nutrient Reports"""

    search = "search"
    """Paginated lists of items matching a query"""


class UsdaNdbListType(Enum):
    """USDA API food or nutrients list settings"""

    all_nutrients = "n"
    """List all known nutrients."""

    specialty_nutrients = "ns"
    """
    List all nutrients not included in the Standard Release database.
    """

    standard_release_nutrients = "nr"
    """
    List all nutrients included in the Standard Release database.
    """

    food = "f"
    """List all food items."""

    food_groups = "g"
    """List all food groups."""

    derivation_codes = "d"
    """List all derivation codes."""


class UsdaNdbReportType(Enum):
    """USDA API food report types"""

    basic = "b"
    """
    Contains a limited set of nutrients,
    like what could be found on a product packaging
    """

    full = "f"
    """Contains all the available nutrients"""

    stats = "s"
    """
    Added statistics data from the Standard Reference database when available.

    .. note::

       The stats report type is currently not fully supported by python-usda.
       It is however possible to get all the returned data using raw methods
       on a :class:`usda.client.UsdaClient` instance.
    """

    @classmethod
    def from_response_data(cls, value):
        return {
            'Basic': cls.basic,
            'Full': cls.full,
            'Statistics': cls.stats,
        }.get(value, value)
