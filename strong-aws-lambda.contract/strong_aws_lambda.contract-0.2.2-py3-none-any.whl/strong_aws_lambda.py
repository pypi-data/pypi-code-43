from functools import wraps
from typing import Type, TypeVar

from strong_aws_pkg.strong_contract_mapper import hydrate_contract
from strong_aws_pkg.strong_custom_resource import LambdaContext

T = TypeVar("T")


def strong_aws_lambda(contract_class: Type[T]):
    def wrapper(function):
        @wraps(function)
        def decorated(event: dict, context: LambdaContext):
            params = hydrate_contract(event, contract_class)
            return_value = function(params, context)

            return return_value

        return decorated

    return wrapper
