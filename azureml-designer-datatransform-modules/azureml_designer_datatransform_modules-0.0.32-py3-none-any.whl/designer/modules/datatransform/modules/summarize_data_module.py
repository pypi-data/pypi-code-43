import pandas as pd
from pandas.api.types import is_datetime64_any_dtype as is_datetime
import numpy as np
import sys
from azureml.designer.modules.datatransform.common.module_base import ModuleBase
from azureml.designer.modules.datatransform.common.module_parameter import ModuleParameters, InputPortModuleParameter, \
    OutputPortModuleParameter
from azureml.designer.modules.datatransform.common.logger import custom_module_logger as logger
from azureml.designer.modules.datatransform.common.logger import format_obj
from azureml.designer.modules.datatransform.common.module_meta_data import ModuleMetaData
from azureml.designer.modules.datatransform.common.module_spec_node import ModuleSpecNode

class SummarizeDataModule(ModuleBase):
    def __init__(self):
        meta_data = ModuleMetaData(
            id="2c57074f-674f-45de-ad85-d84e4726f04e",
            name="Summarize Data",
            category="Statistical Functions",
            description="Generates a basic descriptive statistics report for the columns in a dataset.")
        parameters = ModuleParameters([
            InputPortModuleParameter(
                name="input", friendly_name="Input", is_optional=False),
            OutputPortModuleParameter(
                name="dataset", friendly_name="Result_dataset", is_optional=False)
        ])
        module_nodes= [
            ModuleSpecNode.from_module_parameter(parameters["input"]),
            ModuleSpecNode.from_module_parameter(parameters["dataset"]),
        ]
        conda_config_file = './azureml/designer/modules/datatransform/modules/conda_config/summarize_data_module.yml'
        super().__init__(meta_data=meta_data, parameters=parameters, module_nodes=module_nodes,
                         conda_config_file=conda_config_file)

    def run(self):
        logger.info("Read input data")
        input_data = self._get_input("input")
        logger.info(format_obj("input_data", input_data))
        output = pd.DataFrame()
        for column in input_data.columns:
            output = pd.concat([output, Series_Summarize(input_data[column]).get_summarize()])
        output = SummarizeDataModule._normalize_column(input_data, output)
        logger.info(format_obj("output", output))
        self._handle_output("dataset", output)

    @staticmethod
    def _include_mix_datetime(data:pd.DataFrame):
        include_datetime = [Series_Summarize._is_datetime(data[column]) for column in data]
        return any(include_datetime) and not all(include_datetime)

    @staticmethod
    def _normalize_column(data:pd.DataFrame, output:pd.DataFrame):
        if SummarizeDataModule._include_mix_datetime(data):
            convert_columns = ["Mode","Min","Max", "Mean", "1st quantile", "Median","3rd quantile", "P0.5","P1","P5","P95","P99","P99.5"]
            for column in convert_columns:
                output[column] = output[column].apply(str)
        for column in output.columns:
            column_type = pd.api.types.infer_dtype(output[column])
            if column_type == "integer":
                output[column] = output[column].astype('int64')
            if column_type == "floating":
                output[column] = output[column].astype('float')
            if column_type == "boolean":
                output[column] = output[column].astype('bool')
        return output

class Series_Summarize():
    def __init__(self, ds: pd.Series):
        self._data = ds
        self._is_timedelta = Series_Summarize._is_timedelta(ds)
        self._is_datetime = Series_Summarize._is_datetime(ds)
        self._is_boolean = Series_Summarize._is_boolean(ds)
        self._preprocess_data = Series_Summarize._preprocess_data(ds)

    INT_MAX = sys.maxsize
    INT_MIN = -sys.maxsize-1
    @staticmethod
    def _is_datetime(ds: pd.Series) -> bool:
        return not Series_Summarize._is_timedelta(ds) and pd.core.dtypes.common.is_datetimelike(ds)
    
    @staticmethod
    def _is_timedelta(ds: pd.Series) -> bool:
        return pd.core.dtypes.common.is_timedelta64_dtype(ds)

    @staticmethod
    def _is_boolean(ds: pd.Series) -> bool:
        return ds.dtype.name == "bool"

    @staticmethod
    def _preprocess_data(ds: pd.Series) -> pd.Series:
        if Series_Summarize._is_timedelta(ds):
            return ds.apply(lambda dt: pd.to_timedelta(dt).value).apply(lambda td: td if td != Series_Summarize.INT_MIN else None)
        if Series_Summarize._is_datetime(ds):
            return ds.apply(lambda dt: pd.to_datetime(dt).value).apply(lambda dt:  dt if dt != Series_Summarize.INT_MIN else None)
        if Series_Summarize._is_boolean(ds):
            return ds.apply(lambda dt: 1.0 if dt else 0.0)
        return ds

    def _special_handle(self, fn, return_time_span = False):
        if self._is_boolean:
            return fn(self._preprocess_data)
        if not self._is_datetime and not self._is_timedelta:
            return fn(self._data)
        if self._is_timedelta:
            return None
        if return_time_span:
            return None
        return pd.to_datetime(fn(self._preprocess_data))

    @staticmethod
    def _get_mode_str(ds: pd.Series):
        if ds.size > 1:
            return '{' + ', '.join([str(m)for m in ds]) + '}'
        elif ds.size == 1:
            return str(ds[0])
        return None
    
    def _is_numeric(self) -> bool:
        if np.issubdtype(self._data, np.number) or self._is_timedelta or self._is_datetime:
            return True
        return False
    
    # def _is_boolean(self) -> bool:
    #     return self._is_boolean
        # return self._data.dtype.name == "bool"
    
    def _is_full_process(self) -> bool:
        return self._is_numeric() or self._is_boolean
    
    def _percentile(self, p):
        if self._is_full_process():
            return self._special_handle(lambda x:x.quantile(p/100.0))
        return None
    
    def _range(self):
        if not self._is_full_process():
            return None
        if self._is_numeric() and not self._is_datetime and not self._is_timedelta:
            return self._data.max() - self._data.min()
        if self._data.max() == self._data.min():
            return 0
        if self._is_boolean:
            return 1
        return None

    def get_summarize(self) -> pd.DataFrame:
        functions = {
            "Feature": self._data.name,
            "Count": self._data.count(),
            "Unique Value Count": self._data.nunique(),
            "Missing Value Count": (self._data.isnull()).sum(),
            "Min": self._data.min() if self._is_full_process() else None,
            "Max": self._data.max() if self._is_full_process() else None,
            "Mean":self._special_handle(lambda x: x.mean()) if self._is_full_process()  else None,
            "Mean Deviation":  self._special_handle(lambda x: x.mad()) if self._is_full_process() and not self._is_datetime and not self._is_timedelta else None, # can not output time delta
            "1st quantile": self._percentile(25),
            "Median": self._special_handle(lambda x: x.median()) if self._is_full_process() else None,
            "3rd quantile": self._percentile(75),
            "Mode": Series_Summarize._get_mode_str(self._data.mode()),
            "Range": self._range(),
            "Sample Variance": self._data.var() if self._is_boolean or (not self._is_timedelta and not self._is_datetime and self._is_numeric()) else None, # can not output time delta
            "Sample Standard Deviation": self._special_handle(lambda x:x.std()) if self._is_full_process() and not self._is_datetime and not self._is_timedelta else None,
            "Sample Skewness": self._preprocess_data.skew() if self._is_full_process() else None,
            "Sample Kurtosis": self._preprocess_data.kurt() if self._is_full_process() else None,
            "P0.5": self._percentile(0.5),
            "P1": self._percentile(1),
            "P5": self._percentile(5),
            "P95": self._percentile(95),
            "P99": self._percentile(99),
            "P99.5": self._percentile(99.5),
        }
        data = pd.Series(functions, name=self._data.name).to_frame().T
        return data
