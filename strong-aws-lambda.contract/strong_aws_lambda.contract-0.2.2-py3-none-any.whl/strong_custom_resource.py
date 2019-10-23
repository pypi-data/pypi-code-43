import json
from functools import wraps
from typing import Type

from aws_lambda_context import LambdaContext

from strong_aws_pkg.strong_contract_mapper import hydrate_contract
from strong_aws_pkg.strong_custom_resource_base_contracts import AwsRequestContract, BaseResultErrorContract, \
    TBaseRequestContract
from strong_aws_pkg.json_extension import StrongJson


class InvalidCustomResourceReturnJsonError(ValueError):
    """The return must be a JSON with a key 'STATUS' and the value 'SUCCESS' or 'FAILED'"""

    def __init__(self, message, invalid_return):

        if isinstance(invalid_return, (int, float, bool, str)):
            str_invalid_return = str(invalid_return)
        else:
            str_invalid_return = invalid_return.__class__

        if str_invalid_return:
            message = f'Invalid return "{str_invalid_return}". {message}'

        super().__init__(message)


_INVALID_CUSTOM_RESOURCE_RETURN_JSON_MSG = "The return must be a JSON or an object which can be converted into a JSON " \
                                           "with a key 'STATUS' and the value 'SUCCESS' or 'FAILED'"


def _is_valid_return_json(str_value) -> bool:
    try:
        json_value = json.loads(str_value)
        return_value = json_value['Status']
    except:
        return False

    return return_value in ['SUCCESS', 'FAILED']


def strong_aws_lambda_custom_resource(contract_class: Type[TBaseRequestContract],
                                      handle_untreated_exceptions: bool = True):
    def wrapper(function):
        @wraps(function)
        def decorated(event: dict, context: LambdaContext):
            try:
                resource_properties = event['ResourceProperties']
                params = hydrate_contract(resource_properties, contract_class)
                aws_params = hydrate_contract(event, AwsRequestContract)

                return_value = function(params, context, aws_params)

                try:
                    return_json = StrongJson.dumps(return_value)

                    if not _is_valid_return_json(return_json):
                        raise InvalidCustomResourceReturnJsonError(_INVALID_CUSTOM_RESOURCE_RETURN_JSON_MSG,
                                                                   return_value)

                    return return_json
                except ValueError:
                    raise InvalidCustomResourceReturnJsonError(_INVALID_CUSTOM_RESOURCE_RETURN_JSON_MSG, return_value)

            except Exception as ex:
                if handle_untreated_exceptions:
                    return StrongJson.dumps(BaseResultErrorContract(Reason=str(ex)))

        return decorated

    return wrapper
