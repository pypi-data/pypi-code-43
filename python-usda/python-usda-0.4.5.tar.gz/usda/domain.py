#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from usda.enums import UsdaNdbReportType


class UsdaObject(ABC):
    """
    An abstract base class for all USDA result objects.
    """

    @staticmethod
    @abstractmethod
    def from_response_data(response_data):
        """
        Generate an object from JSON response data.

        :param response_data: Parsed JSON response data from the API.
        :rtype: UsdaObject
        """
        raise NotImplementedError


class ListItem(UsdaObject):
    """
    Describes a USDA list item. A list item is any kind of item that has an
    ID and a name; all results from list API requests are of this type.
    """

    @staticmethod
    def from_response_data(response_data):
        """
        Generate a ListItem from JSON response data.

        :param dict response_data: Parsed JSON response data from the API.
        :rtype: ListItem
        """
        return ListItem(
            id=response_data['id'],
            name=response_data['name'],
        )

    def __init__(self, id, name):
        """
        :param int id: Unique identifier of the list item.
        :param str name: Name of the list item.
        """
        super().__init__()

        self.id = id
        """
        Unique identifier of the list item.

        :type: int
        """

        self.name = str(name)
        """
        Name of the list item.

        :type: str
        """

    def __str__(self):
        return self.name

    def __repr__(self):
        return "{0} ID {1} '{2}'".format(
            self.__class__.__name__, self.id, self.name)


class Food(ListItem):
    """
    Describes a USDA food item, with only an ID and a name.
    Food items from Nutrient Reports are returned as
    :class:`NutrientReportFood` instances.
    """

    @staticmethod
    def from_response_data(response_data):
        """
        Generate a Food instance from JSON response data.

        :param dict response_data: Parsed JSON response data from the API.
        :rtype: Food
        """
        return Food(
            id=response_data['id']
            if 'id' in response_data
            else response_data['ndbno'],
            name=response_data['name'],
        )


class Nutrient(ListItem):
    """
    Describes a USDA nutrient.
    In reports, can hold associated measurement data.
    """

    @staticmethod
    def from_response_data(response_data):
        """
        Generate a Nutrient instance from JSON response data.
        This only parses the ``id`` and ``name`` attributes of nutrients
        returned by list API endpoints; the other properties have to be set
        manually in other methods.

        :param dict response_data: Parsed JSON response data from the API.
        """
        return Nutrient(id=response_data['id'], name=response_data['name'])

    def __init__(self, id, name,
                 group=None, unit=None, value=None, measures=None):
        """
        :param int id: Unique identifier of the nutrient.
        :param str name: Name of the nutrient.
        :param group: Name of the nutrient's group.
        :type group: str or None
        :param unit: Unit in which the nutrient's quantity is expressed.
        :type unit: str or None
        :param value: Quantity of the nutrient, in the context of a report.
        :type value: float or None
        :param measures: Measurements of the nutrient.
        :type measures: list(Measure) or None
        """
        super().__init__(id, name)

        self.group = str(group) if group is not None else None
        """
        Name of the nutrient's group. Is only returned in Food Reports.

        :type: str or None
        """

        self.unit = str(unit) if unit is not None else None
        """
        Unit in which the nutrient's value is expressed.
        Is only returned in Food and Nutrient reports.

        :type: str or None
        """

        self.value = float(value) if value is not None else None
        """
        Quantity of the nutrient for 100 grams of food.
        Is only returned in Food and Nutrient reports.

        :type: float or None
        """

        self.measures = measures
        """
        :class:`Measure` instances describing the various
        available measurements for the nutrient.
        Is only returned in Food and Nutrient reports.

        :type: list(Measure) or None
        """


class Measure(UsdaObject):
    """
    Describes a measurement made for a specific nutrient.
    """

    @staticmethod
    def from_response_data(response_data):
        """
        Generate a Measure instance from JSON response data.

        :param dict response_data: Parsed JSON response data from the API.
        :rtype: Measure
        """
        return Measure(
            quantity=response_data["qty"],
            gram_equivalent=response_data["eqv"],
            label=response_data["label"],
            value=response_data["value"],
        )

    def __init__(self, quantity, gram_equivalent, label, value):
        """
        :param float quantity: Quantity of the volume of food described in
           the label used. Most of the time, equals ``1.0``.
        :param float gram_equivalent: 100 gram equivalent of the measurement.
        :param str label: Describes the measurement.
           Usually holds an indication of the volume of food used.
        :param float value: The measured value.
        """
        super().__init__()
        self.quantity = float(quantity)
        """
        Quantity of the volume of food described in the measurement's label.
        Most of the time, equals 1.

        :type: float
        """

        self.gram_equivalent = float(gram_equivalent)
        """
        100 gram equivalent of the measurement.

        :type: float
        """

        self.label = str(label)
        """
        Describes the measurement.
        Usually holds an indication of the volume of food used.

        :type: str
        """

        self.value = float(value)
        """
        The measured quantity of a nutrient in the volume of food used.

        :type float:
        """

    def __repr__(self):
        return "Measure '{0}': {1} {2}".format(
            self.label, self.value, self.quantity)

    def __str__(self):
        return self.label


class FoodReport(UsdaObject):
    """
    Describes a USDA food report,
    holding a food item's nutritional information.
    """

    @staticmethod
    def _get_measures(raw_measures):
        """Get measurements from JSON data."""
        return list(map(Measure.from_response_data, raw_measures))

    @staticmethod
    def _get_nutrients(raw_nutrients):
        """Get nutrients from JSON data with their associated measurements."""
        return [
            Nutrient(
                id=raw_nutrient["nutrient_id"],
                name=raw_nutrient["name"],
                group=raw_nutrient["group"],
                unit=raw_nutrient["unit"],
                value=raw_nutrient["value"],
                measures=FoodReport._get_measures(raw_nutrient["measures"]),
            )
            for raw_nutrient in raw_nutrients
        ]

    @staticmethod
    def from_response_data(response_data):
        """
        Generate a Food Report from JSON response data.

        :param dict response_data: Parsed JSON response data from the API.
        :rtype: FoodReport
        """
        report = response_data["report"]
        type = report["type"]
        food = report['food']
        food_group = None if type == "Basic" or type == "Statistics" \
            else food["fg"]
        return FoodReport(
            food=Food.from_response_data(food),
            nutrients=FoodReport._get_nutrients(food["nutrients"]),
            report_type=type,
            foot_notes=[
                ListItem(fn['id'], fn['desc']) for fn in report["footnotes"]
            ],
            food_group=food_group,
        )

    def __init__(self, food, nutrients, report_type, foot_notes, food_group):
        """
        :param food: The food item the report is about.
        :type food: Food
        :param nutrients: List of nutrients with measurement data.
        :type nutrients: list(Nutrient)
        :param str report_type: The Food Report's type as a string
           (``Full``, ``Basic`` or ``Statistics``)
        :param foot_notes: A list of foot notes for the report.
        :type foot_notes: list(str) or list(ListItem)
        :param food_group: The food group's name.
        :type food_group: str or None
        """
        super().__init__()

        assert isinstance(food, Food)
        self.food = food
        """
        The food item the report is about.

        :type: Food
        """

        self.nutrients = nutrients
        """
        List of nutrients with measurement data.

        :type: list(Nutrient)
        """

        self.report_type = UsdaNdbReportType.from_response_data(report_type)
        """
        The Food Report's type.

        :type: UsdaNdbReportType
        """

        self.foot_notes = foot_notes
        """
        A list of foot notes for the report.
        In Version 1 Food Reports, is a list of strings.
        In Version 2 Food Reports, is a list of :class:`ListItem`,
        as footnotes are given an ID and a description.

        :type: list(str) or list(ListItem)
        """

        self.food_group = str(food_group) if food_group is not None else None

    def __repr__(self):
        return "{0} for {1}".format(self.__class__.__name__, repr(self.food))


class Source(ListItem):
    """
    Describes a USDA nutrient information source for Food Reports version 2.
    """

    @staticmethod
    def from_response_data(response_data):
        """
        Generate a Source instance from parsed JSON data.

        :param dict response_data: Parsed JSON response data.
        :rtype: Source
        """
        return Source(
            id=response_data['id'],
            title=response_data['title'],
            authors=response_data['authors'],
            vol=response_data['vol'],
            iss=response_data['iss'],
            year=response_data['year'],
        )

    def __init__(self, id, title, authors, vol, iss, year):
        """
        :param str id: Unique identifier for the source.
        :param str title: Title of the article.
        :param str authors: Authors of the source, in a way that could be
           formatted as a bibliography citation.
        :param str vol: Volume where the article was published.
        :param str iss: Issue where the article was published.
        :param str year: Year of publication of the issue.
        """
        super().__init__(id, title)

        self.authors = authors
        """
        Authors of the article, in a way that could be formatted as a
        bibliography citation.

        :type: str
        """

        self.vol = vol
        """
        Volume where the article was published.

        :type: str
        """

        self.iss = iss
        """
        Issue where the article was published.

        :type: str
        """

        self.year = year
        """
        Year of publication of the issue.

        :type: str
        """

    @property
    def title(self):
        """
        Alias for :attr:`ListItem.name`.
        """
        return self.name


class FoodReportV2(FoodReport):
    """
    Describes a USDA food report version 2.
    Compared to version 1 Food Reports, those add Sources in a way that is
    more easily handled by code than footnotes.

    .. note::

       Even if sources are added, footnotes still exist, and are parsed as
       :class:`ListItem` instances instead of strings.
    """

    @staticmethod
    def from_response_data(response_data):
        """
        Generate a Food Report version 2 from JSON response data.

        :param dict response_data: Parsed JSON response data from the API.
        :rtype: FoodReportV2
        """
        food = response_data['food']
        return FoodReportV2(
            food=Food.from_response_data(food['desc']),
            food_group=None,
            report_type=food['type'],
            foot_notes=[
                ListItem(fn['id'], fn['desc']) for fn in food['footnotes']
            ],
            nutrients=FoodReport._get_nutrients(food['nutrients']),
            sources=[
                Source.from_response_data(s)
                for s in food.get('sources', [])
            ],
        )

    def __init__(self, sources, *args, **kwargs):
        r"""
        :param sources: Sources for the food report's data.
        :type sources: list(Source)
        :param \*args: Arguments given to the inherited
           :class:`FoodReport` class.
        :param \**kwargs: Keyword arguments given to the inherited
           :class:`FoodReport` class.
        """
        super().__init__(*args, **kwargs)
        self.sources = sources


class NutrientReportFood(Food):
    """
    Describes a USDA food item holding nutrient data.
    Used in Nutrient Reports.
    """

    def __init__(self, id, name, nutrients):
        """
        :param int id: Unique identifier of the food item.
        :param str name: Name of the food item.
        :param nutrients: Nutrients for the given food item.
        :type nutrients: list(Nutrient)
        """
        super().__init__(id, name)

        assert all(isinstance(nutrient, Nutrient) for nutrient in nutrients)
        self.nutrients = nutrients
        """
        Nutrients for the given food item.

        :type: list(Nutrient)
        """

    @staticmethod
    def from_response_data(response_data):
        """
        Generate a NutrientReportFood instance from parsed JSON data.

        :param dict response_data: Parsed JSON response data.
        :rtype: NutrientReportFood
        """
        food = Food.from_response_data(response_data)
        return NutrientReportFood(food.id, food.name, [
            Nutrient(
                id=nutrient["nutrient_id"],
                name=nutrient["nutrient"],
                unit=nutrient["unit"],
                value=nutrient["value"],
                measures=[
                    Measure(
                        quantity=response_data["weight"],
                        gram_equivalent=nutrient["gm"],
                        label=response_data["measure"],
                        value=nutrient["value"],
                    )
                ],
            )
            for nutrient in response_data["nutrients"]
        ])
