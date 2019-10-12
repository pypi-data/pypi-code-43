import yaml
import logging
import re

from collections import namedtuple
from werkzeug.exceptions import BadRequest
from ingaia.commons import request_util
from decorator import decorator
from .exceptions import NoOpenAPIFileConfiguredException


class ApiConfig:
    """
    Class for work with open api config properties
    """
    _api_info = None
    _config_file = None

    @classmethod
    def set_config_file(cls, openapi_file):
        cls._config_file = openapi_file

    @classmethod
    def load_config_file(cls):
        """
        Loads the api config file
        :return:
        """
        if cls._api_info is None:
            if cls._config_file is None:
                raise NoOpenAPIFileConfiguredException()

            # reads the yaml file
            with open(cls._config_file, 'r') as stream:
                try:
                    api_info = dict(yaml.safe_load(stream))
                    logging.info(f' The file "{cls._config_file}" was successfully loaded')
                except yaml.YAMLError as exc:
                    raise exc
            # convert the dict to an object to export
            cls._api_info = namedtuple("ApiInfo", api_info.keys())(*api_info.values())

    @classmethod
    def config(cls):
        """
        Returns the dict with api configurations
        :return:
        """
        if cls._api_info is None:
            cls.load_config_file()
        return cls._api_info

    @classmethod
    def get_params_by_request_body(cls, request_body_def):
        """
        Gets the request body params based on openapi.yaml definitions
        :param request_body_def: Definition name from yaml file
        :return: Dict for params
        """
        # load the request body parameters
        list_subscription = cls.config().components['requestBodies'][request_body_def]
        list_subscription_params = list_subscription['content']['application/json']['schema']['properties']

        # make the response
        default_params = []
        operators_params = []
        for param in list_subscription_params:
            operator = cls.get_param_operator(param)
            if not operator:
                default_params.append(param)
            else:
                param_value = list_subscription_params[param]
                operator_param = {
                    "param": str(param).replace(operator, '').replace('[]', ''),
                    "enum": param_value["enum"] if "enum" in param_value else None
                }

                # gets supported opertator params
                description = str(param_value['description'])

                # NOTE: for this to work, it's necessary begin the description
                #       with "**Supported params**:" and finish the 'params' with "<br>"
                # Syntax example:
                #   **Supported params**: asc, desc <br>
                supported_params = '**Supported params**:'
                if description.find(supported_params) != 0:
                    logging.warning(f'Description error for "{param}"')
                else:
                    if description.find('<br>') != -1:
                        operators = description[len(supported_params):description.find('<br>')].split(',')
                        operators = [o.strip() for o in operators]
                        operator_param["operators"] = operators

                operators_params.append(operator_param)

        return {
            "default": default_params,
            "operators": operators_params
        }

    @classmethod
    def validate_payload(cls, payload, request_body_def):
        """
        Validates the request body (payload) based on openapi.yaml definitions
        :param payload: Payload received from the request
        :param request_body_def: Definition name from yaml file
        :raise BadRequest if the request body is invalid
        """
        request_body_params = cls.get_params_by_request_body(request_body_def)

        for param in payload.keys():
            in_default_params = True
            if param not in request_body_params['default']:
                in_default_params = False

            in_operators_params = False
            if not in_default_params:
                operator: str = cls.get_param_operator(param)
                if operator:
                    in_operators_params = True
                    cls._validade_operator(param, operator, payload[param], request_body_params)

            if not in_default_params and not in_operators_params:
                raise BadRequest(f'Invalid param "{param}"')

    @classmethod
    def _validade_operator(cls, param, operator, value, request_body_params):
        """
        Validates the param with opertator
        :param operator: Operator received in payload
        :param value: Value received in payload
        :param param: Parameter received in payload
        :param request_body_params: Parameters loaded from api config file
        """
        param = str(param).replace(operator, '').replace('[]', '')
        if 'operators' in request_body_params:
            param_operators = [p["param"] for p in request_body_params['operators']]
            if param in param_operators:
                valid_operators = []
                valid_values = []
                for p in request_body_params['operators']:
                    if p["param"] == param:
                        valid_operators = p["operators"] if "operators" in p else None
                        valid_values = p["enum"] if "enum" in p else None
                        break

                if valid_operators and operator not in valid_operators:
                    raise BadRequest(f'Invalid operator "{operator}" for parameter "{param}"')

                if valid_values and value not in valid_values:
                    raise BadRequest(f'Invalid value "{value}" for parameter "{param}". Valid values: {valid_values}')

    @staticmethod
    def get_param_operator(param) -> str:
        """
        Auxiliary method to receive the operator of a param
        :param param:
        :return:
        """
        matches = re.findall(r'\[(.*?)\]', param)
        return matches[0] if matches else None


@decorator
def validate_payload(fn, request_body_def=None, *args, **kw):
    # recovers the payload
    payload = dict(request_util.get_request_payload())

    # aditional validation
    # validates the payload based on api config file (openapi.yaml)
    ApiConfig.validate_payload(payload, request_body_def)

    # returns the function
    return fn(*args, **kw)
