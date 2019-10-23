#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from usda.enums import UsdaNdbListType, UsdaNdbReportType, UsdaUriActions
from usda.domain import \
    ListItem, Nutrient, Food, FoodReport, FoodReportV2, NutrientReportFood
from usda.base import DataGovClientBase, DataGovApiError
from usda.pagination import \
    RawPaginator, ModelPaginator, RawNutrientReportPaginator


class UsdaClient(DataGovClientBase):
    """
    Describes a USDA NDB API client.
    """

    def __init__(self, api_gov_key):
        """
        :param str api_gov_key: A Data.gov API key.
           For small testing purposes, you may use ``DEMO_KEY`` as an API key;
           but beware of rate limit errors.
        """
        super().__init__('ndb/', api_gov_key)

    def list_nutrients_raw(self, **kwargs):
        r"""
        Get a list of available nutrients in the database as JSON.

        :param \**kwargs: GET parameters to send along the request.
        :returns: Generator yielding nutrients as JSON data.
        :rtype: usda.pagination.RawPaginator
        """
        kwargs.setdefault('lt', UsdaNdbListType.all_nutrients.value)
        return RawPaginator(self, UsdaUriActions.list, **kwargs)

    def list_nutrients(self, max, offset=0, sort='n'):
        """
        Get a list of available nutrients in the database.
        Useful to generate Nutrient Reports.

        :param int max: Maximum number of nutrients to return, up to 1500.
        :param int offset: Index to start listing at.
        :param str sort: The sorting method.
           ``'r'`` for relevance, ``'n'`` for item ID.
        :returns: Generator yielding nutrients as
           :class:`usda.domain.Nutrient` instances.
        :rtype: usda.pagination.ModelPaginator
        """
        return ModelPaginator(
            Nutrient,
            self.list_nutrients_raw(max=max, offset=offset, sort=sort),
        )

    def list_foods_raw(self, **kwargs):
        r"""
        Get a list of available food items in the database as JSON.

        :param \**kwargs: GET parameters to send along the request.
        :returns: Generator yielding food items as JSON data.
        :rtype: usda.pagination.RawPaginator
        """
        kwargs.setdefault('lt', UsdaNdbListType.food.value)
        return RawPaginator(self, UsdaUriActions.list, **kwargs)

    def list_foods(self, max, offset=0, sort='n'):
        """
        Get a list of available food items in the database.
        Useful to generate Food Reports.

        :param int max: Maximum number of items to return, up to 1500.
        :param int offset: Index to start listing at.
        :param str sort: The sorting method.
           ``'r'`` for relevance, ``'n'`` for item ID.
        :returns: Generator yielding food items as
           :class:`usda.domain.Food` instances.
        :rtype: usda.pagination.ModelPaginator
        """
        return ModelPaginator(
            Food,
            self.list_foods_raw(max=max, offset=offset, sort=sort),
        )

    def list_food_groups_raw(self, **kwargs):
        r"""
        Get a list of available food groups in the database as JSON.

        :param \**kwargs: GET parameters to send along the request.
        :returns: Generator yielding food groups as JSON data.
        :rtype: usda.pagination.RawPaginator
        """
        kwargs.setdefault('lt', UsdaNdbListType.food_groups.value)
        return RawPaginator(self, UsdaUriActions.list, **kwargs)

    def list_food_groups(self, max, offset=0, sort='n'):
        """
        Get a list of available food groups in the database.

        :param int max: Maximum number of groups to return, up to 1500.
        :param int offset: Index to start listing at.
        :param str sort: The sorting method.
           ``'r'`` for relevance, ``'n'`` for group ID.
        :returns: Generator yielding food groups as
           :class:`usda.domain.ListItem` instances.
        :rtype: usda.pagination.ModelPaginator
        """
        return ModelPaginator(
            ListItem,
            self.list_food_groups_raw(max=max, offset=offset, sort=sort),
        )

    def list_derivation_codes_raw(self, **kwargs):
        r"""
        Get a list of available derivation codes in the database as JSON.

        :param \**kwargs: GET parameters to send along the request.
        :returns: Generator yielding derivation codes as JSON data.
        :rtype: usda.pagination.RawPaginator
        """
        kwargs.setdefault('lt', UsdaNdbListType.derivation_codes.value)
        return RawPaginator(self, UsdaUriActions.list, **kwargs)

    def list_derivation_codes(self, max, offset=0, sort='n'):
        """
        Get a list of available derivation codes in the database.

        :param int max: Maximum number of codes to return, up to 1500.
        :param int offset: Index to start listing at.
        :param str sort: The sorting method.
           ``'r'`` for relevance, ``'n'`` for code ID.
        :returns: Generator yielding derivation codes as
           :class:`usda.domain.ListItem` instances.
        :rtype: usda.pagination.ModelPaginator
        """
        return ModelPaginator(
            ListItem,
            self.list_derivation_codes_raw(max=max, offset=offset, sort=sort),
        )

    def search_foods_raw(self, **kwargs):
        r"""
        Get a list of food items matching a specified query, as JSON.

        :param \**kwargs: GET parameters to send along the request.
        :returns: Generator yielding food items as JSON data.
        :rtype: usda.pagination.RawPaginator
        """
        return RawPaginator(self, UsdaUriActions.search, **kwargs)

    def search_foods(self, query, max, offset=0, sort='r'):
        """
        Get a list of food items matching a specified query.

        :param str query: A search query.
        :param int max: Maximum number of items to return, up to 1500.
        :param int offset: Index to start listing at.
        :param str sort: The sorting method.
           ``'r'`` for relevance, ``'n'`` for item ID.
        :returns: Generator yielding food items as
           :class:`usda.domain.Food` instances.
        :rtype: usda.pagination.ModelPaginator
        """
        return ModelPaginator(
            Food,
            self.search_foods_raw(q=query, max=max, offset=offset, sort=sort),
        )

    def get_food_report_raw(self, **kwargs):
        r"""
        Get a Food Report for a given food item ID as JSON.

        :param \**kwargs: GET parameters to send along the request.
        :returns: A food report as JSON data.
        :rtype: dict
        :raises requests.exceptions.HTTPError: If a response has a HTTP 4xx or
           5xx status code.
        :raises DataGovApiError: If a Data.gov API returns an error.
        """
        return self.run_request(UsdaUriActions.report, **kwargs)

    def get_food_report(self, ndb_food_id,
                        report_type=UsdaNdbReportType.basic):
        """
        Get a Food Report for a given food item ID.

        :param int ndb_food_id: ID of a food item to get a food report for.
        :param report_type: Food Report type to get.
        :type report_type: usda.enums.UsdaNdbReportType
        :returns: A food report for the given food item ID.
        :rtype: usda.domain.FoodReport
        :raises requests.exceptions.HTTPError: If a response has a HTTP 4xx or
           5xx status code.
        :raises DataGovApiError: If a Data.gov API returns an error.
        """
        return FoodReport.from_response_data(
            self.get_food_report_raw(type=report_type.value, ndbno=ndb_food_id)
        )

    def get_food_report_v2_raw(self, **kwargs):
        r"""
        Get a Food Report version 2 for one or more food item IDs as JSON.

        :param \**kwargs: GET parameters to send along the request.
        :returns: A list of food reports version 2 as JSON data.
        :rtype: dict
        :raises requests.exceptions.HTTPError: If a response has a HTTP 4xx or
           5xx status code.
        :raises DataGovApiError: If a Data.gov API returns an error.
        """
        return self.run_request(UsdaUriActions.v2report, **kwargs)

    def get_food_report_v2(self, *ids, report_type=UsdaNdbReportType.basic):
        r"""
        Get a list of Food Reports version 2 for one or more food item IDs.

        :param int \*ids: Up to 25 food item IDs.
        :param report_type: Food Report type to get.
        :type report_type: usda.enums.UsdaNdbReportType
        :returns: A list of food reports versions 2.
        :rtype: list(usda.domain.FoodReportV2)
        :raises requests.exceptions.HTTPError: If a response has a HTTP 4xx or
           5xx status code.
        :raises DataGovApiError: If a Data.gov API returns an error.
        """
        def _get_report(food):
            if 'error' in food:
                raise DataGovApiError(food['error'])
            return FoodReportV2.from_response_data(food)

        return list(map(
            _get_report,
            self.get_food_report_v2_raw(
                type=report_type.value, ndbno=ids,
            )['foods']
        ))

    def get_nutrient_report_raw(self, **kwargs):
        r"""
        Get a Nutrient Report for each of the given nutrient IDs as JSON.

        :param \**kwargs: GET parameters to send along the request.
        :returns: A generator yielding food items with the specified nutrients
           as JSON data.
        :rtype: usda.pagination.RawNutrientReportPaginator
        """
        return RawNutrientReportPaginator(
            self, UsdaUriActions.nutrients, **kwargs)

    def get_nutrient_report(self, *nutrients):
        r"""
        Get a Nutrient Report for each of the given nutrient IDs.

        :param int \*nutrients: Up to 20 nutrient IDs.
        :returns: A generator yielding food items with the specified nutrients
           as :class:`usda.domain.NutrientReportFood` instances.
        :rtype: usda.pagination.ModelPaginator
        :raises ValueError: If there are more than 20 nutrient IDs.
        :raises requests.exceptions.HTTPError: If a response has a HTTP 4xx or
           5xx status code.
        :raises DataGovApiError: If a Data.gov API returns an error.
        """
        if len(nutrients) > 20:
            raise ValueError("A nutrient report request cannot contain "
                             "more than 20 nutrients")
        return ModelPaginator(
            NutrientReportFood,
            self.get_nutrient_report_raw(nutrients=nutrients),
        )
