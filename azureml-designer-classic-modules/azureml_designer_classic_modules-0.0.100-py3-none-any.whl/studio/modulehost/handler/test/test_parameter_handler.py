import pytest
from azureml.studio.modulehost.attributes import IntParameter, ModeParameter

from azureml.studio.common.error import ParameterParsingError
from azureml.studio.common.types import AutoEnum
from azureml.studio.modulehost.handler.parameter_handler import ParameterHandler


class _Enum(AutoEnum):
    a = 1


@pytest.mark.parametrize(
    'value_string, parameter_annotation',
    [
        ('a', IntParameter()),
        ('b', ModeParameter(_Enum))
    ]
)
def test_parameter_paring_error(value_string, parameter_annotation):
    err_message = f'Failed to convert "value_string" parameter value ' \
        f'"{value_string}" from "str" to "{parameter_annotation.data_type.__name__}".'
    with pytest.raises(ParameterParsingError, match=err_message):
        ParameterHandler().handle_argument_string(value_string, parameter_annotation)
