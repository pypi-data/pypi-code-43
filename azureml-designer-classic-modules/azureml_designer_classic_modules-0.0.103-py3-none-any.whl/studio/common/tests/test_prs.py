from azureml.studio.common.parameter_range import ParameterRangeSettings


def test_prs():
    print(ParameterRangeSettings.from_value(2))
    print(ParameterRangeSettings.from_value(2.0))
    print(ParameterRangeSettings.from_literal('1'))
    print(ParameterRangeSettings.from_literal('1.0'))
    print(ParameterRangeSettings.from_literal('1;2;3'))
    print(ParameterRangeSettings.from_literal('0.1; 0.01; 0.001'))
    print(ParameterRangeSettings.from_literal('1; 0.1; 5-10'))
    print(ParameterRangeSettings.from_json('{"literal":"1, 0.1, 5-10"}'))
