from typing import Tuple, List

class PandasImportError(Exception):
    """
    Exception raised when pandas was not able to be imported.
    """
    _message = 'Could not import pandas. Ensure a compatible version is installed by running: pip install azureml-dataprep[pandas]'
    def __init__(self):
        print('PandasImportError: ' + self._message)
        super().__init__(self._message)


class NumpyImportError(Exception):
    """
    Exception raised when numpy was not able to be imported.
    """
    _message = 'Could not import numpy. Ensure a compatible version is installed by running: pip install azureml-dataprep[pandas]'
    def __init__(self):
        print('NumpyImportError: ' + self._message)
        super().__init__(self._message)


_have_pandas = True
_have_numpy = True
_have_pyarrow = True
try:
    import pandas
except:
    _have_pandas = False
try:
    import numpy
except:
    _have_numpy = False
try:
    import pyarrow
    version_components = pyarrow.__version__.split('.')
    major = int(version_components[0])
    minor = int(version_components[1])
    if major <= 0 and minor < 11:
        _have_pyarrow = False
except:
    _have_pyarrow = False

def have_numpy() -> bool:
    global _have_numpy
    return _have_numpy

def have_pandas() -> bool:
    global _have_pandas
    return _have_pandas

def have_pyarrow() -> bool:
    global _have_pyarrow
    return _have_pyarrow

def _ensure_numpy_pandas():
    if not have_pandas():
        raise PandasImportError()
    if not have_numpy():
        raise NumpyImportError()

def _sanitize_df_for_native(df):
    import pandas as pd
    import numpy as np
    # Ensure column schema is one dimensional and strings.
    if isinstance(df.columns, pd.MultiIndex):
        # Flatten MultiIndex by getting higherarchy as tuples then joining each tuple to a _ seperated string.
        df.columns = ['_'.join(t) for t in df.columns.values]
    else:
        # Cast any non-string index values to be strings.
        df.columns = df.columns.astype(str)
    # Handle Categorical typed columns. Categorical is a pandas type not a numpy type and azureml-dataprep-native can't
    # handle it. This is temporary pending improvments to native that can handle Categoricals, vso: 246011
    new_schema = df.columns.tolist()
    new_values = []
    for column_name in new_schema:
        if pd.api.types.is_categorical_dtype(df[column_name]):
            new_values.append(np.asarray(df[column_name]))
        else:
            new_values.append(df[column_name].values)
    return (new_schema, new_values)


def ensure_df_native_compat(df: 'pandas.DataFrame') -> Tuple[List[str], List]:
    _ensure_numpy_pandas()
    return _sanitize_df_for_native(df)
