from enum import Enum
import pytest
from azureml.designer.modules.datatransform.common.module_base import ModuleBase, EnumArgType, BooleanArgType
from azureml.designer.modules.datatransform.common.module_meta_data import ModuleMetaData
from azureml.designer.modules.datatransform.common.module_parameter import ModuleParameters, ValueModuleParameter
from azureml.studio.internal.error import ParameterParsingError
class MockEnum(Enum):
    Enum1 = "Enum1"
    Enum2 = "Enum2"

class MockModule(ModuleBase):
    def __init__(self):
        meta_data = ModuleMetaData()
        parameters = ModuleParameters([
            ValueModuleParameter(name="para_bool",data_type=bool),
            ValueModuleParameter(name="para_mode",data_type=MockEnum),
        ])
        conda_config_file = None
        super().__init__(meta_data=meta_data ,parameters=parameters, conda_config_file=conda_config_file)

    def run(self):
        pass

def test_arg_parser():
    module = MockModule()
    parser = module.get_arg_parser()
    raw_args = ["TestModule", "--para_bool", "True", "--para_mode", "Enum1"]
    args = parser.parse_args(raw_args)
    assert args.para_mode is MockEnum.Enum1
    assert args.para_bool is True
    module.insert_arguments(**vars(args))
    assert module.parameters["para_bool"].value is True
    assert module.parameters["para_mode"].value is MockEnum.Enum1

@pytest.mark.parametrize("input",["True","true","t","y","Y","1"])
def test_bool_parser_true(input):
    parser = BooleanArgType("input")
    assert parser(input) is True

@pytest.mark.parametrize("input",["False","false","f","F","N","n","0"])
def test_bool_parser_false(input):
    parser = BooleanArgType("input")
    assert parser(input) is False

@pytest.mark.parametrize("input",["xyz","tuz"," "])
def test_bool_parser_exception(input):
    parser = BooleanArgType("input")
    with pytest.raises(ParameterParsingError, match="Failed to convert"):
        parser(input)

@pytest.mark.parametrize("input",["Enum1",MockEnum.Enum1])
def test_enum_parse(input):
    assert EnumArgType(MockEnum,"input")(input) is MockEnum.Enum1

@pytest.mark.parametrize("input",["random"])
def test_enum_parse(input):
    with pytest.raises(ParameterParsingError, match="Failed to convert"):
        assert EnumArgType(MockEnum,"input")(input)