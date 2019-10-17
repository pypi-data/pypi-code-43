import pytest

from azureml.studio.common.error import ErrorMapping, NoColumnsSelectedError, ModuleError, \
    ColumnNotFoundError, GreaterThanError, IncorrectAzureMLDatastoreError


def test_error_with_no_args():
    with pytest.raises(NoColumnsSelectedError,
                       match=r'Specified column set does not apply to any of dataset columns.'):
        ErrorMapping.throw(NoColumnsSelectedError())


def test_error_with_one_arg():
    with pytest.raises(NoColumnsSelectedError,
                       match=r'Specified column set "abc" does not apply to any of dataset columns.'):
        ErrorMapping.throw(NoColumnsSelectedError("abc"))


def test_error_str():
    e0 = ColumnNotFoundError()
    e1 = ColumnNotFoundError('column_name')
    e2 = ColumnNotFoundError('column_name', arg_name_missing_column='def')
    e3 = ColumnNotFoundError('column_name', arg_name_missing_column='def', arg_name_has_column='abc')

    assert str(e0) == 'One or more specified columns were not found.'
    assert str(e1) == 'Column with name or index "column_name" not found.'
    assert str(e2) == 'Column with name or index "column_name" does not exist in "def".'
    assert str(e3) == 'Column with name or index "column_name" does not exist in "def", but exists in "abc".'


def test_positional_error_str():
    e0 = GreaterThanError()
    e1 = GreaterThanError("param_name", 100)

    assert str(e0) == 'Parameter should be greater than boundary value.'
    assert str(e1) == 'Parameter "param_name" value should be greater than 100.'


def test_error_id():
    e0 = ColumnNotFoundError()
    assert e0.id.name == 'ColumnNotFound'

    e1 = GreaterThanError("param_name", 100)
    assert e1.id.name == 'GreaterThan'


def test_bad_class_name_will_raise():
    with pytest.raises(ValueError, match=f"Bad class name 'BadClassName'. Must end with 'Error'."):
        class BadClassName(ModuleError):
            pass


def test_defining_error_class_with_unrecognized_error_id_will_raise():
    with pytest.raises(ValueError, match=f"Unrecognized ErrorId: NonExist"):
        class NonExistError(ModuleError):
            pass


@pytest.mark.skip('Cannot hit this because error in looking up ErrorId will raised first.')
def test_defining_error_class_with_no_xml_entry_will_raise():
    with pytest.raises(ValueError, match=f"No xml entry found for NonExist."):
        class NonExistError(ModuleError):
            pass


def test_args_in_xml_does_not_exist_in_init_func_will_raise():
    with pytest.raises(ValueError, match=f"Argument 'arg_name_missing_column' found in xml message,"
                       f" but does not exist in ColumnNotFoundError.__init__ method as a param. Maybe a typo?"):
        class ColumnNotFoundError(ModuleError):
            def __init__(self, column_id: str = None):
                pass


def test_get_exception_message():
    m0 = ErrorMapping.get_exception_message(ValueError("This is a Value Error"))
    m1 = ErrorMapping.get_exception_message(Exception("This is a Exception"))

    class NoMessageException(Exception):
        status_code = 500

        def __init__(self, message):
            Exception.__init__(self)
            self.message = message

    m2 = ErrorMapping.get_exception_message(NoMessageException("This is a NoMessageException"))

    assert m0 == 'This is a Value Error'
    assert m1 == 'This is a Exception'
    assert m2 == 'NoMessageException()'


def test_error_incorrect_datastore():
    msg = "Datastore information is invalid. Failed to get AzureML datastore 'abc' in workspace 'bcd'."
    with pytest.raises(IncorrectAzureMLDatastoreError, match=msg):
        raise IncorrectAzureMLDatastoreError(datastore_name='abc', workspace_name='bcd')
