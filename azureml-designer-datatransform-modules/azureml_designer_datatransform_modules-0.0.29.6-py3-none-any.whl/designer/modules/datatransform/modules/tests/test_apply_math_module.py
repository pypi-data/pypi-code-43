import mpmath
from scipy import special
import math
import tempfile
import os
import datetime
import random
import pytz
import pytest
import pandas as pd
from azureml.designer.modules.datatransform.tools.sample_data_gen import gen_empty_table
from azureml.designer.modules.datatransform.modules.apply_math_module import ApplyMathModule, MathCategory, OutputMode,\
    BasicFunc, OperationsFunc, CompareFunc, RoundingFunc, SpecialFunc, TrigonometricFunc, OperationArgumentType
from azureml.designer.modules.datatransform.tools.dataframe_utils import compare_dataframe
from azureml.studio.core.utils.column_selection import ColumnSelectionBuilder
from azureml.studio.core.io.data_frame_directory import save_data_frame_to_directory, load_data_frame_from_directory
from azureml.studio.core.data_frame_schema import DataFrameSchema
from azureml.designer.modules.datatransform.tools.column_selection_utils import convert_column_selection_to_json


@pytest.mark.parametrize("output_mode,expect_data_columns", [
    (OutputMode.Append, {"ID": "int", "Age": "int",
                         "Acos(ID)": "int", "Acos(Age)": "int"}),
    (OutputMode.Inpalce, {"ID": "int", "Age": "int"}),
    (OutputMode.ResultOnly, {"Acos(ID)": "int", "Acos(Age)": "int"}),
],
    ids=[
        "Append",
        "Inpalce",
        "ResultOnly"
]
)
def test_empty_table_output_mode(output_mode, expect_data_columns):
    empty_table = gen_empty_table({"ID": "int", "Age": "int"})
    expect_data = gen_empty_table(
        expect_data_columns)
    apply_math_module_test_kernal(
        input_data=empty_table,
        column_selector=convert_column_selection_to_json(ColumnSelectionBuilder().include_all()),
        category=MathCategory.Trigonometric,
        func=TrigonometricFunc.Acos,
        output_mode=output_mode,
        expect_data=expect_data
    )


def test_simple1():
    input_data = pd.DataFrame([[1, 2, 3, 4]], columns=[
                              "one", "two", "three", "four"])
    expect_data = pd.DataFrame([[1, 4, 9, 16]], columns=[
                               "Square(one)", "Square(two)", "Square(three)",  "Square(four)"])
    apply_math_module_test_kernal(
        input_data=input_data,
        column_selector=convert_column_selection_to_json(ColumnSelectionBuilder().include_all()),
        category=MathCategory.Basic,
        func=BasicFunc.Square,
        output_mode=OutputMode.ResultOnly,
        expect_data=expect_data
    )
    expect_data = pd.DataFrame([[1.0, 4.0, 9.0, 16.0]], columns=[
                               "Pow(one_$2.0)", "Pow(two_$2.0)", "Pow(three_$2.0)", "Pow(four_$2.0)"])
    apply_math_module_test_kernal(
        input_data=input_data,
        column_selector=convert_column_selection_to_json(ColumnSelectionBuilder().include_all()),
        category=MathCategory.Basic,
        func=BasicFunc.Pow,
        arg_type=OperationArgumentType.Constant,
        arg_constant=2.0,
        output_mode=OutputMode.ResultOnly,
        expect_data=expect_data
    )
    expect_data = pd.DataFrame([[1, 4, 9, 16]], columns=[
                               "Pow(one_two)", "Pow(two_two)", "Pow(three_two)", "Pow(four_two)"])
    apply_math_module_test_kernal(
        input_data=input_data,
        column_selector=convert_column_selection_to_json(ColumnSelectionBuilder().include_all()),
        category=MathCategory.Basic,
        func=BasicFunc.Pow,
        arg_type=OperationArgumentType.ColumnSet,
        arg_column_selector=convert_column_selection_to_json(ColumnSelectionBuilder().include_col_names("two")),
        output_mode=OutputMode.ResultOnly,
        expect_data=expect_data
    )


@pytest.mark.parametrize("input_data,test_func,expect_data", [
    ([-1], BasicFunc.Abs, 1),
    ([4, 5], BasicFunc.Atan2, 0.674741),
    ([2], BasicFunc.Conj, 2),
    ([27], BasicFunc.Cuberoot, 3.0),
    ([8], BasicFunc.DoubleFactorial, 384),
    ([2], BasicFunc.Eps, 4.440892e-16),
    ([2], BasicFunc.Exp, 7.38905609893065),
    ([2, 3], BasicFunc.Exp2, 12.0),
    ([2], BasicFunc.ExpMinus1, 6.38905609893065),
    ([2], BasicFunc.Factorial, 2),
    ([2, 3], BasicFunc.Hypotenuse, 3.605551275463989),
    ([2], BasicFunc.Ln, 0.6931471805599453),
    ([2], BasicFunc.LnPlus1, 1.0986122886681098),
    ([2, 3], BasicFunc.Log, 0.6309297535714574),
    ([2], BasicFunc.Log10, 0.30102999566398114),
    ([2], BasicFunc.Log2, 1.0),
    ([2, 4], BasicFunc.NthRoot, 1.189207115002721),
    ([2, 4], BasicFunc.Pow, 16),
    ([4], BasicFunc.Sqrt, 2.0),
    ([4], BasicFunc.SqrtPi, 3.5449077018110318),
    ([4], BasicFunc.Square, 16),
])
def test_basic(input_data, test_func, expect_data):
    with_extra_arg = len(input_data) > 1
    input_data = pd.DataFrame([input_data], columns=(
        ["x", "y"] if with_extra_arg else ['x']))
    expect_column_name = f"{test_func.value}(x_y)" if with_extra_arg else f"{test_func.value}(x)"
    expect_data = pd.DataFrame([[expect_data]], columns=[expect_column_name])
    assert apply_math_module_test_kernal(
        input_data=input_data,
        column_selector=convert_column_selection_to_json(ColumnSelectionBuilder().include_col_names("x")),
        category=MathCategory.Basic,
        func=test_func,
        arg_type=OperationArgumentType.ColumnSet if with_extra_arg else None,
        arg_column_selector=convert_column_selection_to_json(ColumnSelectionBuilder().include_col_names("y")) if with_extra_arg else None,
        output_mode=OutputMode.ResultOnly,
        expect_data=expect_data
    )


@pytest.fixture
def compare_func_dataframe():
    return pd.DataFrame(data=[
        [1, 2],
        [3, 3],
        [2, 1],
        [-1, -3]
    ], columns=["x", "y"])

@pytest.mark.parametrize("compare_func,expect_data", [
    (CompareFunc.EqualTo, [[False], [True], [False], [False]]),
    (CompareFunc.GreaterThan, [[False], [False], [True], [True]]),
    (CompareFunc.GreaterThanOrEqualTo, [[False], [True], [True], [True]]),
    (CompareFunc.LessThan, [[True], [False], [False], [False]]),
    (CompareFunc.LessThanOrEqualTo, [[True], [True], [False], [False]]),
    (CompareFunc.NotEqualTo, [[True], [False], [True], [True]]),
    (CompareFunc.PairMax, [[2], [3], [2], [-1]]),
    (CompareFunc.PairMin, [[1], [3], [1], [-3]]),
],
    ids=[
        "EqualTo",
        "GreaterThan",
        "GreaterThanOrEqualTo",
        "LessThan",
        "LessThanOrEqualTo",
        "NotEqualTo",
        "PairMax",
        "PairMin"
]
)
def test_compare(compare_func_dataframe, compare_func, expect_data):
    expect_data = pd.DataFrame(expect_data, columns=[
                               f"{compare_func.value}(x_y)"])
    assert apply_math_module_test_kernal(
        input_data=compare_func_dataframe,
        column_selector=convert_column_selection_to_json(ColumnSelectionBuilder().include_col_names("x")),
        category=MathCategory.Compare,
        func=compare_func,
        arg_type=OperationArgumentType.ColumnSet,
        arg_column_selector=convert_column_selection_to_json(ColumnSelectionBuilder(
        ).include_col_names("y")),
        output_mode=OutputMode.ResultOnly,
        expect_data=expect_data
    )


@pytest.fixture
def operation_func_dataframe():
    return pd.DataFrame(data=[
        [1, 2.0],
    ], columns=["x", "y"])

@pytest.mark.parametrize("operation_func,expect_data", [
    (OperationsFunc.Add, [[3.0]]),
    (OperationsFunc.Divide, [[0.5]]),
    (OperationsFunc.Multiply, [[2.0]]),
    (OperationsFunc.Subtract, [[-1.0]]),
],
    ids=[
        "Add",
        "Divide",
        "Multiply",
        "Subtract"
]
)
def test_operation(operation_func_dataframe, operation_func, expect_data):
    expect_data = pd.DataFrame(expect_data, columns=[
                               f"{operation_func.value}(x_y)"])
    assert apply_math_module_test_kernal(
        input_data=operation_func_dataframe,
        column_selector=convert_column_selection_to_json(ColumnSelectionBuilder().include_col_names("x")),
        category=MathCategory.Operations,
        func=operation_func,
        arg_type=OperationArgumentType.ColumnSet,
        arg_column_selector=convert_column_selection_to_json(ColumnSelectionBuilder(
        ).include_col_names("y")),
        output_mode=OutputMode.ResultOnly,
        expect_data=expect_data
    )


@pytest.fixture
def round_dataframe():
    return pd.DataFrame(data=[
        [1.45, 1],
        [1.44, 1],
        [2.54, 1],
        [3.55, 1],
        [-3.55, 1],
    ], columns=["Value", "Digits"])


@pytest.mark.parametrize("round_func,expect_data", [
    (RoundingFunc.Ceiling, [[2], [2], [3], [4], [-3]]),
    (RoundingFunc.Floor, [[1], [1], [2], [3], [-4]]),
    (RoundingFunc.Mod, [[1.], [1.], [2.], [3.], [-4.]]),
    (RoundingFunc.Quotient, [[1.], [1], [2.], [3.], [-4.]]),
    (RoundingFunc.Remainder, [[0.45], [0.44], [0.54], [0.55], [-0.55]]),
    (RoundingFunc.RoundDigits, [[1.5], [1.4], [2.5], [3.6], [-3.6]]),
    (RoundingFunc.RoundDown, [[1.4], [1.4], [2.5], [3.5], [-3.6]]),
    (RoundingFunc.RoundUp, [[1.5], [1.5], [2.6], [3.6], [-3.5]]),
    (RoundingFunc.ToMultiple, [[1.], [1.], [3.], [4.], [-4.]]),
    (RoundingFunc.Truncate, [[1.4], [1.4], [2.5], [3.5], [-3.5]]),
], ids=[
    "Ceiling",
    "Floor",
    "Mod",
    "Quotient",
    "Remainder",
    "RoundDigits",
    "RoundDown",
    "RoundUp",
    "ToMultiple",
    "Truncate"
])
def test_rounding(round_dataframe, round_func, expect_data):
    expect_data = pd.DataFrame(expect_data, columns=[
        f"{round_func.value}(Value_Digits)"])
    assert apply_math_module_test_kernal(
        input_data=round_dataframe,
        column_selector=convert_column_selection_to_json(ColumnSelectionBuilder().include_col_names("Value")),
        category=MathCategory.Rounding,
        func=round_func,
        arg_type=OperationArgumentType.ColumnSet,
        arg_column_selector=convert_column_selection_to_json(ColumnSelectionBuilder(
        ).include_col_names("Digits")),
        output_mode=OutputMode.ResultOnly,
        expect_data=expect_data
    )


@pytest.fixture
def special_func_dataframe():
    return pd.DataFrame(data=[
        [1.0, 2.0],
    ], columns=["x", "y"])


@pytest.mark.parametrize("special_func,with_columns_selector,expect_data", [
    (SpecialFunc.Beta, True, [[special.beta(1.0, 2.0)]]),
    (SpecialFunc.BetaLn, True, [[special.betaln(1.0, 2.0)]]),
    (SpecialFunc.EllipticIntegralE, False, [[special.ellipk(1.0)]]),
    (SpecialFunc.EllipticIntegralK, False, [[special.ellipe(1.0)]]),
    (SpecialFunc.Erf, False, [[special.erf(1.0)]]),
    (SpecialFunc.Erfc, False, [[special.erfc(1.0)]]),
    (SpecialFunc.ErfcScaled, False, [[special.erfcx(1.0)]]),
    (SpecialFunc.ErfInverse, False, [[special.erfinv(1.0)]]),
    (SpecialFunc.ExponentialIntegralEin, False, [[special.expi(1.0)]]),
    (SpecialFunc.Gamma, False, [[special.gamma(1.0)]]),
    (SpecialFunc.GammaLn, False, [[special.gammaln(1.0)]]),
    (SpecialFunc.GammaRegularizedP, True, [[special.gammainc(1.0, 2.0)]]),
    (SpecialFunc.GammaRegularizedPInverse,
     True, [[special.gammaincinv(1.0, 2.0)]]),
    (SpecialFunc.GammaRegularizedQ, True, [[special.gammaincc(1.0, 2.0)]]),
    (SpecialFunc.GammaRegularizedQInverse,
     True, [[special.gammainccinv(1.0, 2.0)]]),
    (SpecialFunc.Polygamma, True, [[special.polygamma(1.0, 2.0).item(0)]]),
],
    ids=[
        "Beta",
        "BetaLn",
        "EllipticIntegralE",
        "EllipticIntegralK",
        "Erf",
        "Erfc",
        "ErfcScaled",
        "ErfInverse",
        "ExponentialIntegralEin",
        "Gamma",
        "GammaLn",
        "GammaRegularizedP",
        "GammaRegularizedPInverse",
        "GammaRegularizedQ",
        "GammaRegularizedQInverse",
        "Polygamma",
]
)
def test_special(special_func_dataframe, special_func, with_columns_selector, expect_data):

    expect_data = pd.DataFrame(expect_data, columns=[
                               f"{special_func.value}(x_y)" if with_columns_selector else f"{special_func.value}(x)"])
    assert apply_math_module_test_kernal(
        input_data=special_func_dataframe,
        column_selector=convert_column_selection_to_json(ColumnSelectionBuilder().include_col_names("x")),
        category=MathCategory.Special,
        func=special_func,
        arg_type=OperationArgumentType.ColumnSet if with_columns_selector else None,
        arg_column_selector=convert_column_selection_to_json(ColumnSelectionBuilder(
        ).include_col_names("y")) if with_columns_selector else None,
        output_mode=OutputMode.ResultOnly,
        expect_data=expect_data
    )


def trigonometric_func_test_parameters():
    parameter_mapping = {
        TrigonometricFunc.Acos: 0.5,
        TrigonometricFunc.Acosh: 2.0,
        TrigonometricFunc.Acot: 2.0,
        TrigonometricFunc.Acoth: 2.0,
        TrigonometricFunc.Acsc: 2.0,
        TrigonometricFunc.Acsch: 2.0,
        TrigonometricFunc.Arg: 2.0,
        TrigonometricFunc.Asec: 2.0,
        TrigonometricFunc.AcscDegrees: 180,
        TrigonometricFunc.AsecDegrees: 180,
        TrigonometricFunc.RadiansToDegrees: 1.0,
        TrigonometricFunc.DegreesToRadians: 30.0
    }
    result_mapping = {
        TrigonometricFunc.DegreesToRadians: math.radians(30.0),
        TrigonometricFunc.RadiansToDegrees: math.degrees(1.0),
        TrigonometricFunc.Acos: ApplyMathModule.convert_mpmath_result(mpmath.acos(0.5)),
        TrigonometricFunc.AcosDegrees: ApplyMathModule.convert_mpmath_result(
            mpmath.acos(math.radians(30.0)))
    }
    skip_func = {TrigonometricFunc.Cis}
    parameters = [(
        parameter_mapping[func] if func in parameter_mapping else (
            30.0 if func.value.endswith("Degrees") else 1.0),
        func,
        [[result_mapping[func]]] if func in result_mapping else None
    ) for func in list(TrigonometricFunc) if not func in skip_func]
    return parameters

@pytest.mark.parametrize("input_value, trigonometric_func, expect_data", trigonometric_func_test_parameters(), ids=[func.value for func in TrigonometricFunc if not func in {TrigonometricFunc.Cis}]
                         )
def test_trignometric(input_value, trigonometric_func, expect_data):
    input_data = pd.DataFrame(data=[
        [input_value]], columns=["x"])
    if expect_data:
        expect_data = pd.DataFrame(expect_data, columns=[
                                   f"{trigonometric_func.value}(x)"])
    assert apply_math_module_test_kernal(
        input_data=input_data,
        column_selector=convert_column_selection_to_json(ColumnSelectionBuilder().include_col_names("x")),
        category=MathCategory.Trigonometric,
        func=trigonometric_func,
        output_mode=OutputMode.ResultOnly,
        expect_data=expect_data
    )


def apply_math_module_test_kernal(
    input_data: pd.DataFrame,
    column_selector: str,
    category: MathCategory,
    func,
    arg_type: OperationArgumentType = None,
    arg_column_selector: str = None,
    arg_constant: float = None,
    output_mode: OutputMode = OutputMode.Append,
    expect_data: pd.DataFrame = None
):
    import time
    with tempfile.TemporaryDirectory(dir=".") as tmpdirname:
        input_path = os.path.join(tmpdirname,  'input_data\\')
        schema = DataFrameSchema.data_frame_to_dict(input_data)
        save_data_frame_to_directory(input_path, data=input_data, schema=schema)
        # input_path = os.path.join(tmpdirname,  'input_data\\data.parquet')
        # os.makedirs(os.path.dirname(input_path))
        # input_data.to_parquet(input_path)
        # output_path = os.path.join(tmpdirname, 'output\\data.parquet')
        output_path = os.path.join(tmpdirname, 'output\\')
        module = ApplyMathModule()
        arguments = {
            "input": os.path.dirname(input_path),
            "category": category,
            "column_selector": column_selector,
            f"{category.value.lower()}_func": func,
            "output_mode": output_mode,
            'dataset': os.path.dirname(output_path)
        }
        if category != MathCategory.Trigonometric:
            if arg_type:
                arguments[f"{category.value.lower()}_arg_type"] = arg_type
            if arg_column_selector:
                arguments[f"{category.value.lower()}_column_selector"] = arg_column_selector
            if arg_constant:
                arguments[f"{category.value.lower()}_constant"] = arg_constant
        module.insert_arguments(**(arguments))
        module.train()
        result = load_data_frame_from_directory(output_path).data
        # result = pd.read_parquet(output_path)
        if expect_data is None:
            return True
        return compare_dataframe(result, expect_data)
        time.sleep(1)
