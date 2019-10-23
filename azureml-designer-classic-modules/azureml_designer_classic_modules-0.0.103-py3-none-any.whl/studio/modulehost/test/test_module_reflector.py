import uuid

import pytest

from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.modulehost.attributes import ModuleMeta
from azureml.studio.common.utils.retry_utils import retry
from azureml.studio.modulehost.module_reflector import BaseModule, module_entry, is_valid_module_entry
from azureml.studio.modules.controlflow.profile_dataset.profile_dataset import ProfileDatasetModule


class TestModule(BaseModule):
    def func_with_no_decorator(self):
        pass

    @retry
    def func_with_wrong_decorator(self):
        pass

    @retry(ValueError, tries=4)
    def func_with_wrong_decorator_with_param(self):
        pass

    @module_entry()
    def func_decorator_arg_is_empty(self):
        pass

    @module_entry(None)
    def func_decorator_arg_is_none(self):
        pass

    @module_entry(meta="abc")
    def func_decorator_arg_is_wrong_type(self):
        pass

    @module_entry(meta=ModuleMeta(name="name", family_id=uuid.uuid4().hex))
    def func_decorator_arg_is_correct_type(self):
        pass

    @retry(ValueError, tries=4)
    @module_entry(meta=ModuleMeta(name="name", family_id=uuid.uuid4().hex))
    def func_with_other_decorator_before_module_entry(self):
        pass

    @module_entry(meta=ModuleMeta(name="name", family_id=uuid.uuid4().hex))
    @retry(ValueError, tries=4)
    def func_with_other_decorator_after_module_entry(self):
        pass


class StaticTestModule(BaseModule):
    @staticmethod
    def func_with_no_decorator():
        pass

    @staticmethod
    @retry
    def func_with_wrong_decorator(self):
        pass

    @staticmethod
    @retry(ValueError, tries=4)
    def func_with_wrong_decorator_with_param(self):
        pass

    @staticmethod
    @module_entry()
    def func_decorator_arg_is_empty():
        pass

    @staticmethod
    @module_entry(None)
    def func_decorator_arg_is_none():
        pass

    @staticmethod
    @module_entry(meta="abc")
    def func_decorator_arg_is_wrong_type():
        pass

    @staticmethod
    @module_entry(meta=ModuleMeta(name="name", family_id=uuid.uuid4().hex))
    def func_decorator_arg_is_correct_type():
        pass

    @staticmethod
    @retry(ValueError, tries=4)
    @module_entry(meta=ModuleMeta(name="name", family_id=uuid.uuid4().hex))
    def func_with_other_decorator_before_module_entry(self):
        pass

    @staticmethod
    @module_entry(meta=ModuleMeta(name="name", family_id=uuid.uuid4().hex))
    @retry(ValueError, tries=4)
    def func_with_other_decorator_after_module_entry(self):
        pass


err_wrong_decorator = "must have a @module_entry decorator"
err_no_parameter = "@module_entry must have a ModuleMeta parameter"
err_wrong_param_type = "@module_entry's parameter is expected to be a ModuleMeta type but got"


def test_is_valid_module_entry():
    assert not is_valid_module_entry(TestModule.func_with_no_decorator)

    assert not is_valid_module_entry(TestModule.func_with_wrong_decorator)

    with pytest.raises(ValueError, match=err_wrong_decorator):
        is_valid_module_entry(TestModule.func_with_wrong_decorator_with_param)

    with pytest.raises(ValueError, match=err_no_parameter):
        is_valid_module_entry(TestModule.func_decorator_arg_is_empty)

    with pytest.raises(ValueError, match=err_no_parameter):
        is_valid_module_entry(TestModule.func_decorator_arg_is_none)

    with pytest.raises(TypeError, match=err_wrong_param_type):
        is_valid_module_entry(TestModule.func_decorator_arg_is_wrong_type)

    assert is_valid_module_entry(TestModule.func_decorator_arg_is_correct_type)

    assert is_valid_module_entry(TestModule.func_with_other_decorator_before_module_entry)

    assert is_valid_module_entry(TestModule.func_with_other_decorator_after_module_entry)


def test_is_valid_module_entry_for_static_methods():
    assert not is_valid_module_entry(StaticTestModule.func_with_no_decorator)

    assert not is_valid_module_entry(StaticTestModule.func_with_wrong_decorator)

    with pytest.raises(ValueError, match=err_wrong_decorator):
        is_valid_module_entry(StaticTestModule.func_with_wrong_decorator_with_param)

    with pytest.raises(ValueError, match=err_no_parameter):
        is_valid_module_entry(StaticTestModule.func_decorator_arg_is_empty)

    with pytest.raises(ValueError, match=err_no_parameter):
        is_valid_module_entry(StaticTestModule.func_decorator_arg_is_none)

    with pytest.raises(TypeError, match=err_wrong_param_type):
        is_valid_module_entry(StaticTestModule.func_decorator_arg_is_wrong_type)

    assert is_valid_module_entry(StaticTestModule.func_decorator_arg_is_correct_type)

    assert is_valid_module_entry(TestModule.func_with_other_decorator_before_module_entry)

    assert is_valid_module_entry(TestModule.func_with_other_decorator_after_module_entry)


def test_bare_decorators_will_raise():
    err_bare_decorator = "@module_entry decorator must contain a ModuleMeta parameter"

    with pytest.raises(ValueError, match=err_bare_decorator):
        class TestBareDecorator:
            @module_entry
            def func(self):
                pass
            pass

    with pytest.raises(ValueError, match=err_bare_decorator):
        class TestBareDecoratorWithStaticMethod:
            @staticmethod
            @module_entry
            def func(self):
                pass
            pass


def test_module_with_no_entry_will_raise():
    with pytest.raises(ValueError, match="No module entry found in TestModule."):
        class TestModule(BaseModule):
            pass


def test_table_name_is_set_when_invoking_module():
    data_table = DataTable()

    assert data_table.name is None

    # The DataTable's name is set when invoking module in @module_entry decorator.
    # This test item is to verify this logic is working.
    # For detailed information refer to PR 268589
    result, = ProfileDatasetModule.run(
        data_table=data_table,
    )

    assert result == data_table
    assert result.name == 'Dataset'
