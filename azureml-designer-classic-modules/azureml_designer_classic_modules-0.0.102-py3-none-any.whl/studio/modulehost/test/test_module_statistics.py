from azureml.studio.common.error import ColumnNotFoundError
from azureml.studio.modulehost.module_reflector import ModuleStatistics


def test_set_error_info_with_module_error():
    module_statistics = ModuleStatistics()
    input_error = ColumnNotFoundError(column_id=0, arg_name_missing_column='data')
    module_statistics.error_info = input_error
    expect_dict = {
        'Exception': {
            'ErrorId': 'ColumnNotFound',
            'ErrorCode': 1,
            'ExceptionType': 'ModuleException',
            'Message': 'ColumnNotFound: Column with name or index "0" does not exist in "data".',
            'Traceback': [
                "Traceback (most recent call last):",
                "  ColumnNotFoundError: Column with name or index \"0\" does not exist in \"data\"."
            ]
        }
    }
    assert module_statistics.error_info == expect_dict


def test_set_error_info_with_python_error():
    module_statistics = ModuleStatistics()
    input_error = TypeError('Invalid input type')
    module_statistics.error_info = input_error
    expect_dict = {
        'Exception': {
            'ExceptionType': 'LibraryException',
            'ErrorId': 'TypeError',
            'ErrorCode': 1000,
            'Message': f'Library Error - TypeError: Invalid input type',
            'Traceback': [
                "Traceback (most recent call last):",
                "  TypeError: Invalid input type"
            ]
        }
    }
    assert module_statistics.error_info == expect_dict


def test_set_error_info_with_traceback():
    module_statistics = ModuleStatistics()
    try:
        try:
            raise TypeError("L3")
        except Exception as e:
            raise ValueError("L2") from e
    except Exception as e:
        module_statistics.error_info = e
    data = module_statistics.error_info['Exception']
    tb_keywords = [
        "Traceback (most recent call last):",
        ", in test_set_error_info_with_traceback",
        "    raise TypeError(\"L3\")",
        "",
        "  TypeError: L3",
        "",
        "The above exception was the direct cause of the following exception:",
        "",
        "Traceback (most recent call last):",
        ", in test_set_error_info_with_traceback",
        "    raise ValueError(\"L2\") from e",
        "      > e = ValueError('L2',)",
        "",
        "  ValueError: L2"
    ]
    assert 'Traceback' in data
    assert len(tb_keywords) == len(data['Traceback'])
    for keyword, trace in zip(tb_keywords, data['Traceback']):
        assert keyword in trace
