import uuid

import pytest
import json

from azureml.studio.modulehost.attributes import ParameterRangeParameter, IntParameter, FloatParameter, \
    BooleanParameter, StringParameter, ColumnPickerParameter, ModeParameter, ItemInfo, \
    ModuleMeta, ReleaseState, ZipInputPort, \
    InputPort, DataTableInputPort, ILearnerInputPort, IClusterInputPort, ITransformInputPort, IFilterInputPort, \
    OutputPort, DataTableOutputPort, ILearnerOutputPort, IClusterOutputPort, ITransformOutputPort, IFilterOutputPort
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.json_encoder import EnhancedJsonEncoder
from azureml.studio.common.types import AutoEnum, get_enum_values
from azureml.studio.common.datatypes import DataTypes


def _print_as_json(d):
    print(json.dumps(d, indent=4, cls=EnhancedJsonEncoder))


class CleanMissingDataHandlingPolicy(AutoEnum):
    ReplaceUsingMICE: ItemInfo(name="Replace using MICE", friendly_name="Replace using MICE") = ()
    ReplaceWithValue: ItemInfo(name="Custom substitution value", friendly_name="Custom substitution value") = ()
    ReplaceWithMean: ItemInfo(name="Replace with mean", friendly_name="Replace with mean") = ()
    ReplaceWithMedian: ItemInfo(name="Replace with median", friendly_name="Replace with median") = ()
    ReplaceWithMode: ItemInfo(name="Replace with mode", friendly_name="Replace with mode") = ()
    RemoveRow: ItemInfo(name="Remove entire row", friendly_name="Remove entire row") = ()
    RemoveColumn: ItemInfo(name="Remove entire column", friendly_name="Remove entire column") = ()
    ReplaceUsingProbabilisticPca: ItemInfo(name="Replace using Probabilistic PCA",
                                           friendly_name="Replace using Probabilistic PCA") = ()


class ColumnsWithAllValuesMissing(AutoEnum):
    Propagate = ()
    Remove = ()


@pytest.mark.parametrize("p", [
    StringParameter(
        name="String Parameter",
        description="A simple test case for string parameter",
    ),
    IntParameter(
        name="Int Parameter",
        description="A simple test case for int parameter",
    ),
    FloatParameter(
        name="Float Parameter",
        description="A simple test case for float parameter",
    ),
    BooleanParameter(
        name="Boolean Parameter",
        description="A simple test case for boolean parameter",
    ),
    ColumnPickerParameter(
        name="Column Picker Parameter",
        description="A simple test case for column picker parameter",
        column_picker_for="ABC",
        single_column_selection=True,
        column_selection_categories=[],
    ),
    ModeParameter(
        ColumnsWithAllValuesMissing,
        name='Cols with all missing values',
        is_optional=False,
        parent_parameter='Cleaning mode',
        parent_parameter_val=[
            CleanMissingDataHandlingPolicy.ReplaceUsingMICE,
            CleanMissingDataHandlingPolicy.ReplaceWithMean,
            CleanMissingDataHandlingPolicy.ReplaceWithMedian,
            CleanMissingDataHandlingPolicy.ReplaceWithMode],
        default_value=ColumnsWithAllValuesMissing.Remove,
        description='Cols with all missing values',
    ),
    ParameterRangeParameter(
        name="Parameter Range Parameter",
        description="A simple test case for parameter range parameter",
    ),
])
def test_parameter_to_dict(p):
    print(f'{p.__class__.__name__}:')
    d = p.to_dict()
    _print_as_json(d)


def test_module_meta_to_dict():
    m = ModuleMeta(
        name="ModuleMeta",
        description="A simple ModuleMeta test sample",
        category="Category 1",
        version="0.0.1",
        owner="Microsoft Corporation",
        family_id=str(uuid.uuid4()),
        release_state=ReleaseState.Release,
    )
    d = m.to_dict()
    _print_as_json(d)
    assert d['ReleaseState'] == ReleaseState.Release


@pytest.mark.parametrize("p", get_enum_values(DataTypes))
def test_data_types(p):
    d = p.value.to_dict()
    _print_as_json(d)


@pytest.mark.parametrize("p", [
    InputPort(
        data_type=DataTable,
        allowed_data_types=[DataTypes.GENERIC_CSV, DataTypes.GENERIC_CSV_NO_HEADER],
        name="Input Dataset",
        friendly_name="Input Dataset Display Name",
        is_optional=True,
        description="Description for InputPort",
    ),
    DataTableInputPort(
        name="DataTableInputPort",
        friendly_name="DataTableInputPort Display Name",
        is_optional=True,
        description="Description for DataTableInputPort",
    ),
    ZipInputPort(
        name="ZipInputPort",
        friendly_name="ZipInputPort Display Name",
        is_optional=True,
        description="Description for ZipInputPort",
    ),
    ILearnerInputPort(
        name="ILearnerInputPort",
        friendly_name="ILearnerInputPort Display Name",
        is_optional=True,
        description="Description for ILearnerInputPort",
    ),
    IFilterInputPort(
        name="IFilterInputPort",
        friendly_name="IFilterInputPort Display Name",
        is_optional=True,
        description="Description for IFilterInputPort",
    ),
    ITransformInputPort(
        name="ITransformInputPort",
        friendly_name="ITransformInputPort Display Name",
        is_optional=True,
        description="Description for ITransformInputPort",
    ),
    IClusterInputPort(
        name="IClusterInputPort",
        friendly_name="IClusterInputPort Display Name",
        is_optional=True,
        description="Description for IClusterInputPort",
    ),
])
def test_input_port(p):
    d = p.to_dict()
    _print_as_json(d)


@pytest.mark.parametrize("p", [
    OutputPort(
        return_type=DataTypes.GENERIC_CSV,
        name="Output Dataset",
        friendly_name="Output Dataset Display Name",
        description="Description for OutputPort",
    ),
    DataTableOutputPort(
        name="DataTableOutputPort",
        friendly_name="DataTableOutputPort Display Name",
        description="Description for DataTableOutputPort",
    ),
    DataTableOutputPort(
        data_type=DataTypes.GENERIC_CSV,
        name="DataTableOutputPort",
        friendly_name="DataTableOutputPort Display Name",
        description="Description for DataTableOutputPort",
    ),
    DataTableOutputPort(
        data_type=DataTypes.GENERIC_CSV_NO_HEADER,
        name="DataTableOutputPort",
        friendly_name="DataTableOutputPort Display Name",
        description="Description for DataTableOutputPort",
    ),
    ILearnerOutputPort(
        name="ILearnerOutputPort",
        friendly_name="ILearnerOutputPort Display Name",
        description="Description for ILearnerOutputPort",
    ),
    IFilterOutputPort(
        name="IFilterOutputPort",
        friendly_name="IFilterOutputPort Display Name",
        description="Description for IFilterOutputPort",
    ),
    ITransformOutputPort(
        name="ITransformOutputPort",
        friendly_name="ITransformOutputPort Display Name",
        description="Description for ITransformOutputPort",
    ),
    IClusterOutputPort(
        name="IClusterOutputPort",
        friendly_name="IClusterOutputPort Display Name",
        description="Description for IClusterOutputPort",
    ),
])
def test_output_port(p):
    d = p.to_dict()
    _print_as_json(d)
