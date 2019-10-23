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
        ('a', IntParameter(name='param_a')),
        ('b', ModeParameter(_Enum, name='param_b')),
    ]
)
def test_parameter_paring_error(value_string, parameter_annotation):
    err_message = f'Failed to convert "{parameter_annotation.name}" parameter value ' \
        f'"{value_string}" from "str" to "{parameter_annotation.data_type.__name__}".'
    with pytest.raises(ParameterParsingError, match=err_message):
        ParameterHandler().handle_argument_string(value_string, parameter_annotation)
