from enum import Enum
import math
import mpmath
import cmath
from inspect import signature
from functools import reduce
from operator import mul
from decimal import Decimal
from typing import List
import numpy as np
from scipy import special
import pandas as pd
from azureml.designer.modules.datatransform.common.module_base import ModuleBase, ModuleMetaData
from azureml.designer.modules.datatransform.common.module_parameter import InputPortModuleParameter, OutputPortModuleParameter, \
    ValueModuleParameter, PercentileValueModuleParameter, ColumnSelectorModuleParameter, ModuleParameters
from azureml.studio.core.utils.column_selection import ColumnSelectionBuilder, ColumnType
from azureml.designer.modules.datatransform.common.logger import custom_module_logger as logger
from azureml.designer.modules.datatransform.common.logger import format_obj
from azureml.designer.modules.datatransform.common.module_spec_node import ModuleSpecNode
from azureml.studio.internal.error import ErrorMapping, BadNumberOfSelectedColumnsError, ParameterParsingError
from azureml.designer.modules.datatransform.tools.column_selection_utils import convert_column_selection_to_json

class MathCategory(Enum):
    Basic = "Basic"
    Compare = "Compare"
    Operations = "Operations"
    Rounding = "Rounding"
    Special = "Special"
    Trigonometric = "Trigonometric"


class BasicFunc(Enum):
    Abs = "Abs"
    Atan2 = "Atan2"
    Conj = "Conj"
    Cuberoot = "Cuberoot"
    DoubleFactorial = "DoubleFactorial"
    Eps = "Eps"
    Exp = "Exp"
    Exp2 = "Exp2"
    ExpMinus1 = "ExpMinus1"
    Factorial = "Factorial"
    Hypotenuse = "Hypotenuse"
    ImaginaryPart = "ImaginaryPart"
    Ln = "Ln"
    LnPlus1 = "LnPlus1"
    Log = "Log"
    Log10 = "Log10"
    Log2 = "Log2"
    NthRoot = "NthRoot"
    Pow = "Pow"
    RealPart = "RealPart"
    Sqrt = "Sqrt"
    SqrtPi = "SqrtPi"
    Square = "Square"


class CompareFunc(Enum):
    EqualTo = "EqualTo"
    GreaterThan = "GreaterThan"
    GreaterThanOrEqualTo = "GreaterThanOrEqualTo"
    LessThan = "LessThan"
    LessThanOrEqualTo = "LessThanOrEqualTo"
    NotEqualTo = "NotEqualTo"
    PairMax = "PairMax"
    PairMin = "PairMin"


class OperationsFunc(Enum):
    Add = "Add"
    Divide = "Divide"
    Multiply = "Multiply"
    Subtract = "Subtract"


class RoundingFunc(Enum):
    Ceiling = "Ceiling"
    CeilingPower2 = "CeilingPower2"
    Floor = "Floor"
    Mod = "Mod"
    Quotient = "Quotient"
    Remainder = "Remainder"
    RoundDigits = "RoundDigits"
    RoundDown = "RoundDown"
    RoundUp = "RoundUp"
    ToEven = "ToEven"
    ToMultiple = "ToMultiple"
    ToOdd = "ToOdd"
    Truncate = "Truncate"


class SpecialFunc(Enum):
    Beta = "Beta"
    BetaLn = "BetaLn"
    EllipticIntegralE = "EllipticIntegralE"
    EllipticIntegralK = "EllipticIntegralK"
    Erf = "Erf"
    Erfc = "Erfc"
    ErfcScaled = "ErfcScaled"
    ErfInverse = "ErfInverse"
    ExponentialIntegralEin = "ExponentialIntegralEin"
    Gamma = "Gamma"
    GammaLn = "GammaLn"
    GammaRegularizedP = "GammaRegularizedP"
    GammaRegularizedPInverse = "GammaRegularizedPInverse"
    GammaRegularizedQ = "GammaRegularizedQ"
    GammaRegularizedQInverse = "GammaRegularizedQInverse"
    Polygamma = "Polygamma"


class TrigonometricFunc(Enum):
    Acos = "Acos"
    AcosDegrees = "AcosDegrees"
    Acosh = "Acosh"
    Acot = "Acot"
    AcotDegrees = "AcotDegrees"
    Acoth = "Acoth"
    Acsc = "Acsc"
    AcscDegrees = "AcscDegrees"
    Acsch = "Acsch"
    Arg = "Arg"
    Asec = "Asec"
    AsecDegrees = "AsecDegrees"
    Asech = "Asech"
    Asin = "Asin"
    AsinDegrees = "AsinDegrees"
    Asinh = "Asinh"
    Atan = "Atan"
    AtanDegrees = "AtanDegrees"
    Atanh = "Atanh"
    Cis = "Cis"
    Cos = "Cos"
    CosDegrees = "CosDegrees"
    Cosh = "Cosh"
    Cot = "Cot"
    CotDegrees = "CotDegrees"
    Coth = "Coth"
    Csc = "Csc"
    CscDegrees = "CscDegrees"
    Csch = "Csch"
    DegreesToRadians = "DegreesToRadians"
    RadiansToDegrees = "RadiansToDegrees"
    Sec = "Sec"
    SecDegrees = "SecDegrees"
    Sech = "Sech"
    Sign = "Sign"
    Sin = "Sin"
    Sinc = "Sinc"
    SinDegrees = "SinDegrees"
    Sinh = "Sinh"
    Tan = "Tan"
    TanDegrees = "TanDegrees"
    Tanh = "Tanh"


class OutputMode(Enum):
    Append = "Append"
    Inpalce = "Inpalce"
    ResultOnly = "ResultOnly"


class OperationArgumentType(Enum):
    Constant = "Constant"
    ColumnSet = "ColumnSet"


class ApplyMathModule(ModuleBase):



    _OPS_FUNC_MAPPING = {
        BasicFunc.Abs: abs,
        BasicFunc.Atan2: lambda x, y: math.atan2(x, y),
        BasicFunc.Conj: lambda x: np.conj(x), # meaningless for real number
        BasicFunc.Cuberoot: lambda x: np.cbrt(x),
        BasicFunc.DoubleFactorial: lambda x: reduce(mul, range(x, 1, -2)),
        BasicFunc.Eps: lambda x: np.spacing(x),
        BasicFunc.Exp: math.exp,
        BasicFunc.Exp2: lambda x, y: np.exp2(x) * y,
        BasicFunc.ExpMinus1: math.expm1,
        BasicFunc.Factorial: math.factorial,
        BasicFunc.Hypotenuse: lambda x, y: math.hypot(x, y),
        BasicFunc.ImaginaryPart: np.imag, #meaningless for real number
        BasicFunc.Ln: lambda x: math.log(x),
        BasicFunc.LnPlus1: lambda x: math.log(x + 1),
        BasicFunc.Log: lambda x, y: math.log(x, y),
        BasicFunc.Log10: lambda x: math.log(x, 10),
        BasicFunc.Log2: lambda x: math.log(x, 2),
        BasicFunc.NthRoot: lambda x, y: x**(1/float(y)),
        BasicFunc.Pow: lambda x, y: pow(x, y),
        BasicFunc.RealPart: np.real, #meaningless for real number
        BasicFunc.Sqrt: lambda x: np.sqrt(x),
        BasicFunc.SqrtPi: lambda x: np.sqrt(x * math.pi),
        BasicFunc.Square: lambda x: np.square(x),
        CompareFunc.EqualTo: lambda x, y: x == y,
        CompareFunc.GreaterThan: lambda x, y: x > y,
        CompareFunc.GreaterThanOrEqualTo: lambda x, y: x >= y,
        CompareFunc.LessThan: lambda x, y: x < y,
        CompareFunc.LessThanOrEqualTo: lambda x, y: x <= y,
        CompareFunc.NotEqualTo: lambda x, y: x != y,
        CompareFunc.PairMax: lambda x, y: np.amax([x, y]),
        CompareFunc.PairMin: lambda x, y: np.amin([x, y]),
        OperationsFunc.Add: lambda x, y: x + y,
        OperationsFunc.Divide: lambda x, y: x / y,
        OperationsFunc.Multiply: lambda x, y: x * y,
        OperationsFunc.Subtract: lambda x, y: x - y,
        RoundingFunc.Ceiling: lambda x, y: math.ceil(x / y) * y,
        RoundingFunc.CeilingPower2: lambda x: math.ceil(x)**2,
        RoundingFunc.Floor: lambda x, y: math.floor(x / y) * y,
        RoundingFunc.Mod: lambda x, y: x // y,
        RoundingFunc.Quotient: lambda x, y: x // y,
        RoundingFunc.Remainder: lambda x, y: float(Decimal(x) % Decimal(y)),
        RoundingFunc.RoundDigits: lambda x, y: int(x*(10**y) + math.copysign(0.5, x))/(10.0**y),
        RoundingFunc.RoundDown: lambda x, y: math.floor(x * (10**y))/(10.0**y),
        RoundingFunc.RoundUp: lambda x, y: math.ceil(x * (10**y))/(10.0**y),
        RoundingFunc.ToEven: lambda x: round(x/2.) * 2,
        RoundingFunc.ToMultiple: lambda x, y: (x + y/2.0) // y * y,
        RoundingFunc.ToOdd: lambda x: x // 2 * 2 + 1,
        RoundingFunc.Truncate: lambda x, y: float(f'%.{y}f' % (x)),
        SpecialFunc.Beta: lambda x, y: special.beta(x, y),
        SpecialFunc.BetaLn: lambda x, y: special.betaln(x, y),
        SpecialFunc.EllipticIntegralE: lambda x: special.ellipk(x),
        SpecialFunc.EllipticIntegralK: lambda x: special.ellipe(x),
        SpecialFunc.Erf: lambda x: special.erf(x),
        SpecialFunc.Erfc: lambda x: special.erfc(x),
        SpecialFunc.ErfcScaled: lambda x: special.erfcx(x),
        SpecialFunc.ErfInverse: lambda x: special.erfinv(x),
        SpecialFunc.ExponentialIntegralEin: lambda x: special.expi(x),
        SpecialFunc.Gamma: lambda x: special.gamma(x),
        SpecialFunc.GammaLn: lambda x: special.gammaln(x),
        SpecialFunc.GammaRegularizedP: lambda x, y: special.gammainc(x, y),
        SpecialFunc.GammaRegularizedPInverse: lambda x, y: special.gammaincinv(x, y),
        SpecialFunc.GammaRegularizedQ: lambda x, y: special.gammaincc(x, y),
        SpecialFunc.GammaRegularizedQInverse: lambda x, y: special.gammainccinv(x, y),
        SpecialFunc.Polygamma: lambda x, y: special.polygamma(x, y).item(0),
        TrigonometricFunc.Cis: lambda x: cmath.rect(1, x), #meaningless for real number
        TrigonometricFunc.DegreesToRadians: math.radians,
        TrigonometricFunc.RadiansToDegrees: math.degrees,
    }

    _EXTRA_ARG_OP_MAPPING = {
        MathCategory.Basic: [BasicFunc.Log, BasicFunc.NthRoot, BasicFunc.Pow, BasicFunc.Atan2, BasicFunc.Exp2, BasicFunc.Hypotenuse],
        MathCategory.Compare: list(CompareFunc),
        MathCategory.Operations: list(OperationsFunc),
        MathCategory.Rounding: [RoundingFunc.Ceiling, RoundingFunc.Floor, RoundingFunc.Mod, RoundingFunc.Quotient, RoundingFunc.Remainder, RoundingFunc.RoundDigits, RoundingFunc.RoundDown, RoundingFunc.RoundUp, RoundingFunc.ToMultiple, RoundingFunc.Truncate],
        MathCategory.Special: [SpecialFunc.Beta, SpecialFunc.BetaLn, SpecialFunc.GammaRegularizedP, SpecialFunc.GammaRegularizedQ,
                               SpecialFunc.GammaRegularizedP, SpecialFunc.GammaRegularizedPInverse, SpecialFunc.GammaRegularizedQInverse, SpecialFunc.Polygamma]
    }

    _MPMATH_SUPPORTED = (TrigonometricFunc.Acos,TrigonometricFunc.AcosDegrees,TrigonometricFunc.Acosh,TrigonometricFunc.Acot,TrigonometricFunc.AcotDegrees,TrigonometricFunc.Acoth,TrigonometricFunc.Acsc,TrigonometricFunc.AcscDegrees,TrigonometricFunc.Acsch,TrigonometricFunc.Arg,TrigonometricFunc.Asec,TrigonometricFunc.AsecDegrees,TrigonometricFunc.Asech,TrigonometricFunc.Asin,TrigonometricFunc.AsinDegrees,TrigonometricFunc.Asinh,TrigonometricFunc.Atan,TrigonometricFunc.AtanDegrees,TrigonometricFunc.Atanh,TrigonometricFunc.Cos,TrigonometricFunc.CosDegrees,TrigonometricFunc.Cosh,TrigonometricFunc.Cot,TrigonometricFunc.CotDegrees,TrigonometricFunc.Coth,TrigonometricFunc.Csc,TrigonometricFunc.CscDegrees,TrigonometricFunc.Csch,TrigonometricFunc.Sec,TrigonometricFunc.SecDegrees,TrigonometricFunc.Sech,TrigonometricFunc.Sign,TrigonometricFunc.Sin,TrigonometricFunc.Sinc,TrigonometricFunc.SinDegrees,TrigonometricFunc.Sinh,TrigonometricFunc.Tan,TrigonometricFunc.TanDegrees,TrigonometricFunc.Tanh)


    @staticmethod
    def _call_mpmath_by_name(func_name:str, x):
        if func_name.endswith("Degrees"):
            method_to_call = getattr(mpmath, func_name[:-7].lower())
            return ApplyMathModule.convert_mpmath_result(method_to_call(math.radians(x)))
        method_to_call = getattr(mpmath, func_name.lower())
        return ApplyMathModule.convert_mpmath_result(method_to_call(x))

    @staticmethod
    def convert_mpmath_result(value):
        if isinstance(value, mpmath.ctx_mp_python.mpf):
            return float(value)
        if isinstance(value, mpmath.ctx_mp_python.mpc):
            raise ValueError("Do not support complex data type.")
            # return complex(value)

    def __init__(self):
        meta_data = ModuleMetaData(
            id="6bd12c13-d9c3-4522-94d3-4aa44513af57",
            name="Apply Math Operation",
            category="Data Transformation\\Manipulation",
            description="Applies a mathematical operation to column values.")
        parameter_list = [
            InputPortModuleParameter(name="input", friendly_name="Input"),
            ColumnSelectorModuleParameter(name="column_selector", friendly_name="Column set", default_value=convert_column_selection_to_json(ColumnSelectionBuilder().include_col_types(ColumnType.NUMERIC))),
            ValueModuleParameter(name="category", friendly_name="Category", data_type=MathCategory, default_value=MathCategory.Basic),
            ValueModuleParameter(name="basic_func", friendly_name="Basic math function", data_type=BasicFunc, default_value=BasicFunc.Abs),
            ValueModuleParameter(name="operations_func", friendly_name="Arithmetic operation", 
                                 data_type=OperationsFunc, default_value=OperationsFunc.Add),
            ValueModuleParameter(name="compare_func", friendly_name="Comparison function", data_type=CompareFunc, default_value=CompareFunc.EqualTo),
            ValueModuleParameter(name="rounding_func", friendly_name="Rounding operation", data_type=RoundingFunc, default_value=RoundingFunc.Ceiling),
            ValueModuleParameter(name="special_func", friendly_name="Special Function", data_type=SpecialFunc, default_value=SpecialFunc.Beta),
            ValueModuleParameter(name="trigonometric_func", friendly_name="Trigonometric Function", 
                                 data_type=TrigonometricFunc, default_value=TrigonometricFunc.Acos),
            OutputPortModuleParameter(
                name="dataset", friendly_name="Result_dataset", is_optional=False)
        ]
        for category in MathCategory:
            if category == MathCategory.Trigonometric:
                continue
            category_string = category.value.lower()
            second_argument_type_name = "Second argument type"
            second_argument_name = "Second argument"
            if category == MathCategory.Compare: 
                second_argument_type_name = "Value to compare type"
                second_argument_name = "Value to compare"
            elif category == MathCategory.Rounding:
                second_argument_type_name = "Precision type"
                second_argument_name = "Precision"
            parameter_list.extend([
                ValueModuleParameter(
                    name=f"{category_string}_arg_type", friendly_name=second_argument_type_name,  data_type=OperationArgumentType, default_value=OperationArgumentType.Constant),
                ColumnSelectorModuleParameter(
                    name=f"{category_string}_column_selector", friendly_name=f"Second argument", default_value=convert_column_selection_to_json(ColumnSelectionBuilder().include_col_types(ColumnType.NUMERIC))),
                ValueModuleParameter(
                    name=f"{category_string}_constant", friendly_name=f"Second argument", data_type=float if category != MathCategory.Rounding else int, default_value=0),
            ])
        parameter_list.append(ValueModuleParameter(
            name="output_mode", friendly_name="Output mode", data_type=OutputMode, default_value=OutputMode.Append))
        parameters = ModuleParameters(parameter_list)
        # Bind input port
        parameters["column_selector"].bind_input(parameters["input"])
        for category in MathCategory:
            if category == MathCategory.Trigonometric:
                continue
            category_string = category.value.lower()
            parameters[f"{category_string}_column_selector"].bind_input(parameters["input"])
        # Construct module node & dependency
        module_node_category = ModuleSpecNode.from_module_parameter(parameters["category"])
        for category in MathCategory:
            category_string = category.value.lower()
            module_node_func = ModuleSpecNode.from_module_parameter(parameters[f"{category_string}_func"], parent_node = module_node_category, options = [category])
            if category == MathCategory.Trigonometric:
                continue
            module_node_arg_type = ModuleSpecNode.from_module_parameter(parameters[f"{category_string}_arg_type"], parent_node = module_node_category if category in [MathCategory.Compare, MathCategory.Operations] else module_node_func, options = [category] if category in [MathCategory.Compare, MathCategory.Operations] else self._EXTRA_ARG_OP_MAPPING[category])

            module_node_column_selector = ModuleSpecNode.from_module_parameter(parameters[f"{category_string}_column_selector"], parent_node = module_node_arg_type, options = [OperationArgumentType.ColumnSet])

            module_node_constant = ModuleSpecNode.from_module_parameter(parameters[f"{category_string}_constant"], parent_node = module_node_arg_type, options = [OperationArgumentType.Constant])
        module_nodes = [
            ModuleSpecNode.from_module_parameter(parameters["input"]),
            module_node_category, 
            ModuleSpecNode.from_module_parameter(parameters["column_selector"]),
            ModuleSpecNode.from_module_parameter(parameters["dataset"]),
            ModuleSpecNode.from_module_parameter(parameters["output_mode"])
        ]
        conda_config_file = './azureml/designer/modules/datatransform/modules/conda_config/apply_math_module.yml'
        super().__init__(meta_data=meta_data, parameters=parameters, module_nodes = module_nodes,
                         conda_config_file=conda_config_file)

    def run(self):
        input_data = self._get_input("input")
        # data_df = self._implement_column_selector(
        #     "column_selector", input_data)
        data_df = self._get_input("column_selector")
        output = self._run_op(input_data=input_data, data_df=data_df)
        result = self._prepare_result(
            input_data=input_data, output=output, op_columns=data_df.columns)
        logger.info(format_obj("output", result))
        self._handle_output("dataset", result)

    @property
    def _output_mode(self):
        return self.parameters["output_mode"].value

    def _run_op(self, input_data: pd.DataFrame, data_df: pd.DataFrame) -> pd.DataFrame:
        operation_type = self.parameters["category"].value
        operation_name = self.parameters[f"{operation_type.value.lower()}_func"].value
        operation_arg_type = None if operation_type == MathCategory.Trigonometric \
            else self.parameters[f"{operation_type.value.lower()}_arg_type"].value
        if operation_arg_type is None:
            output = self._no_arg_op(data_df=data_df, op_name=operation_name)
        elif operation_arg_type == OperationArgumentType.Constant:
            extra_arg = self.parameters[f"{operation_type.value.lower()}_constant"].value
            output = self._const_arg_op(
                data_df=data_df, op_name=operation_name, const=extra_arg)
        else:
            # arg_df = self._implement_column_selector(
            #     f"{operation_type.value.lower()}_column_selector", input_data)
            arg_df = self._get_input(f"{operation_type.value.lower()}_column_selector")
            output = self._column_select_arg_op(
                data_df=data_df, op_name=operation_name, arg_df=arg_df, output_mode=self._output_mode)
        return output

    def _prepare_result(self, input_data: pd.DataFrame, op_columns: List[str], output: pd.DataFrame) -> pd.DataFrame:
        output_mode = self._output_mode
        if output_mode == OutputMode.Append:
            return pd.concat([input_data, output], axis=1)
        if output_mode == OutputMode.ResultOnly:
            return output
        input_data[op_columns] = output
        return input_data

    def _operator(self, op_name, *args):
        if None in args:
            return None
        if op_name in self._MPMATH_SUPPORTED:
            return ApplyMathModule._call_mpmath_by_name(op_name.value, *args)
        if op_name in self._OPS_FUNC_MAPPING.keys():
            return self._OPS_FUNC_MAPPING[op_name](*args)
        # raise NotImplementedError()
        ErrorMapping.throw(ParameterParsingError(op_name))

    def _no_arg_op(self, data_df: pd.DataFrame, op_name) -> pd.DataFrame:
        result = data_df.applymap(lambda x: self._operator(op_name, x))
        result = result.rename(
            columns={column: f"{op_name.value}({column})" for column in result})
        return result

    def _const_arg_op(self, data_df: pd.DataFrame, op_name, const: float) -> pd.DataFrame:
        result = data_df.applymap(lambda x: self._operator(op_name, x, const))
        result = result.rename(
            columns={column: f"{op_name.value}({column}_${const})" for column in result})
        return result

    def _column_select_arg_op(self, data_df: pd.DataFrame, op_name, arg_df: pd.DataFrame, output_mode: OutputMode) -> pd.DataFrame:
        arg_column_count = len(arg_df.columns)
        data_column_count = len(data_df.columns)
        if len(data_df.columns) != 1 and len(arg_df.columns) != 1 and len(data_df.columns) != len(arg_df.columns):
            ErrorMapping.throw(BadNumberOfSelectedColumnsError(self._parameters["column_selector"].friendly_name, exp_col_count=len(arg_df.columns),act_col_count=len(data_df.colums)))
        elif len(data_df.columns) == 1 and len(arg_df.columns) != 1 and output_mode == OutputMode.Inpalce:
            ErrorMapping.throw(BadNumberOfSelectedColumnsError(self._parameters["column_selector"].friendly_name, exp_col_count=len(arg_df.columns),act_col_count=len(data_df.colums)))
        output_df = pd.DataFrame()
        if arg_column_count == 1 or data_column_count == 1:
            for data_column_name in data_df:
                data_column = data_df[data_column_name]
                for arg_column_name in arg_df:
                    arg_column = arg_df[arg_column_name]
                    result_ds = self._op_2_columns(
                        data_column, arg_column, op_name)
                    output_df[result_ds.name] = result_ds
        else:
            for column_index in range(0, data_column_count):
                data_column = data_df.iloc[:, column_index]
                arg_column = arg_df.iloc[:, column_index]
                result_ds = self._op_2_columns(
                    data_column, arg_column, op_name)
                output_df[result_ds.name] = result_ds
        return output_df

    def _op_2_columns(self, data1: pd.Series, data2: pd.Series, op_name) -> pd.Series:
        return pd.Series(data=[self._operator(op_name, v1, v2) for v1, v2 in zip(data1.values.tolist(), data2.values.tolist())], name=op_name.value + "(" + data1.name + "_" + data2.name + ")")

    def _check_column_element_type(self, df: pd.DataFrame):
        pass
