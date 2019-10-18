import pytest
from azureml.designer.modules.datatransform.common.module_parameter import ModuleParameterBase, ValueModuleParameter
from azureml.designer.modules.datatransform.common.tests.test_module_base import MockEnum
from azureml.studio.internal.error import ErrorMapping, NotInRangeValueError, ParameterParsingError

def test_module_parameter_base_validate_pass():
    param = ValueModuleParameter(name="test1", data_type = int)
    param.insert_argument(1)
    assert param.value is 1

def test_module_parameter_base_validate_fail():
    param = ValueModuleParameter(name="test1", data_type = int)
    # with pytest.raises(ValueError):
    #     assert param.validate()
    with pytest.raises(ParameterParsingError):
        assert param.insert_argument("1.0")

# @pytest.mark.parametrize("child_value,parent_value",[(1,TestEnum.Enum1),(None, TestEnum.Enum2)])
# def test_module_parameter_base_dependency_validate_pass(child_value, parent_value):
#     param_child = ValueModuleParameter(name="test1", data_type = int)
#     param_parent = ValueModuleParameter(name="test2", data_type = TestEnum)
#     param_child.parameter_dependencies = ModuleParameterDependencies([
#         ModuleParameterDependency({
#             param_parent: [TestEnum.Enum1]
#         })
#     ])
#     param_child.insert_argument(child_value)
#     param_parent.insert_argument(parent_value)
#     param_child.validate()
#     param_parent.validate()

# @pytest.mark.parametrize("child_value,parent_value",[(1,TestEnum.Enum2),(None, TestEnum.Enum1)])
# def test_module_parameter_base_dependency_validate_fail(child_value, parent_value):
#     param_child = ValueModuleParameter(name="test1", data_type = int)
#     param_parent = ValueModuleParameter(name="test2", data_type = TestEnum)
#     param_child.parameter_dependencies = ModuleParameterDependencies([
#         ModuleParameterDependency({
#             param_parent: [TestEnum.Enum1]
#         })
#     ])
#     param_child.insert_argument(child_value)
#     param_parent.insert_argument(parent_value)
#     param_parent.validate()
#     with pytest.raises(ValueError):
#         param_child.validate()