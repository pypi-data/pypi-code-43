import re

from typing import List
from flask import request

from schemazer.base import (SchemazerParameter, SchemazerHeader,
                            SchemazerCookie, SchemazerSystemParameter)
from schemazer.messages import (ERROR_WRONG, ERROR_INTERVAL, ERROR_TYPE,
                                ERROR_MISSING)
from schemazer.commons.errors import RequestErrors


class RequestValidator:
    """
    The class implements methods for verifying the query parameters for API
    """

    @staticmethod
    def validate_required(parameter: SchemazerParameter, check_type,
                          **kwargs):
        """
        Check in request required parameter
        :param SchemazerParameter parameter: Schema parameter
        :param check_type: Schema parameter
        """
        if (not kwargs.get(parameter.name) and parameter.required
                and parameter.default is None):
            return RequestErrors.BadRequest.json_abort(
                failure_field=parameter.name,
                extend_msg=ERROR_MISSING.format(
                    parameter.name,
                    check_type.__description__))

        return True

    def base_validate(
            self, parameters: List[SchemazerParameter], check_type, **kwargs):
        """
        Validate request parameters by schema.
        Check required parameters and parameter format.
        :param List[SchemazerParameter] parameters: Schema parameters
        :param check_type: Schema parameters
        :return: True if all parameters is correct, or abort response.
        """
        for parameter in parameters or []:
            result = self.validate_required(parameter, check_type, **kwargs)
            if result is not True:
                return result

            value = kwargs.get(parameter.name, parameter.default)
            if value is not None:
                result = parameter.validator.check(
                    parameter=parameter,
                    check_type=check_type,
                    value=value)
            if result is not True:
                return result

        return True

    @staticmethod
    def validate_interval(parameters: List[SchemazerParameter], check_type,
                          **kwargs):
        """
        Validate request parameters by available values interval
        :param List[SchemazerParameter] parameters: Schema parameters
        :param check_type: Header, cookie or query_params
        :param kwargs: Args for validate
        """
        for parameter in parameters or list():
            value = kwargs.get(parameter.name)
            if callable(parameter.interval) and not parameter.interval(value):
                return RequestErrors.BadRequest.json_abort(
                    failure_field=parameter.name,
                    extend_msg=ERROR_INTERVAL.format(
                        parameter.name, check_type.__description__))

        return True

    @staticmethod
    def set_default_values(parameters: List[SchemazerParameter], check_type,
                           **kwargs):
        """
        :param parameters: Schema parameters
        :param check_type: Header, cookie or query_params
        :param kwargs: Args for validate
        """

        for parameter in parameters or []:
            value = kwargs.get(parameter.name)
            value = str(value) if value is not None else None

            try:
                if value or parameter.default:
                    kwargs[parameter.name] = parameter.type(value) \
                        if value is not None else parameter.default
            except ValueError:
                return RequestErrors.BadRequest.json_abort(
                    failure_field=parameter.name,
                    extend_msg=ERROR_TYPE.format(
                        parameter.name,
                        check_type.__description__))

        if check_type.__name__ == SchemazerHeader.__name__:
            request.query.meta.headers = kwargs
        if check_type.__name__ == SchemazerCookie.__name__:
            request.query.meta.cookies = kwargs
        if check_type.__name__ == SchemazerParameter.__name__:
            request.query.args = kwargs
        if check_type.__name__ == SchemazerSystemParameter.__name__:
            request.query.meta.systems = kwargs

        return True

    def process(self, parameters: List[SchemazerParameter], check_type,
                **kwargs):
        """
        Validate request parameters by schema.
        - validate required parameters
        - validate format pattern of parameters
        - validate parameters interval
        - validate params types, convert from string query params by schema
          parameter types.
        :param parameters: Schema parameters
        :param check_type: Header, cookie or query_params
        :param kwargs: Args for validate
        """
        for func in [self.base_validate, self.validate_interval,
                     self.set_default_values]:
            result = func(parameters, check_type, **kwargs)
            if type(result) is not bool:
                return result

        return True


class PatternValidator:
    """
    Regex validator.
    """
    def __init__(self, pattern: str):
        self.pattern = pattern

    @staticmethod
    def _regular_check(value, expression):
        process = re.compile(expression)

        if type(value) in [bool, int, float]:
            value = str(value).lower()
        result = process.match(value)

        return bool(result)

    def check(self, parameter: SchemazerParameter, check_type, value):
        """
        Check request parameter by pattern.
        :param SchemazerParameter parameter: SchemazerParameter schema
        :param check_type: Header, cookie or query_params
        :param value: Parameter value for check
        """
        if not self._regular_check(str(value), self.pattern):
            return RequestErrors.BadRequest.json_abort(
                failure_field=parameter.name,
                extend_msg=ERROR_WRONG.format(
                    parameter.name,
                    check_type.__description__))

        return True
