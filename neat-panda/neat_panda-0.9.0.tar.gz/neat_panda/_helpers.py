import pandas as pd
from warnings import warn
import toml


def _control_types(
    _df,
    _key,
    _value,
    _fill="NaN",
    _convert=False,
    _sep=None,
    _columns=[],
    _drop_na=False,
    _invert_columns=False,
):
    # spread and gather
    if not isinstance(_df, pd.DataFrame):
        raise TypeError("write something")
    if not isinstance(_key, str):
        raise TypeError()
    if not isinstance(_value, str):
        raise TypeError()
    # spread
    if isinstance(_fill, bool):
        raise TypeError()
    if not isinstance(_fill, (str, float, int)):
        raise TypeError()
    if not isinstance(_convert, bool):
        raise TypeError()
    if not isinstance(_sep, (str, type(None))):
        raise TypeError()
    # gather
    if not isinstance(_columns, (list, range)):
        raise TypeError()
    if isinstance(_columns, range) and len(_df.columns) - 1 < _columns[-1]:
        raise IndexError()
    if not isinstance(_drop_na, bool):
        raise TypeError()
    if not isinstance(_invert_columns, bool):
        raise TypeError()


def _assure_consistent_value_dtypes(new_df, old_df, columns, value):
    """
    """
    _dtype = old_df[value].dtypes
    _error_columns = []
    for col in columns:
        try:
            new_df[col] = new_df[col].astype(_dtype)
        except ValueError:
            new_df[col] = new_df[col].astype("O")
            _error_columns.append(col)
            continue
    if _error_columns:
        warn(
            UserWarning(
                f"""Atleast one NaN is generated in the following columns: {", ".join(_error_columns)}. Hence, the type of these columns is set to Object."""
            )
        )
    return new_df


def _custom_columns(columns, new_columns, key, sep):
    _cols = [i for i in columns if i not in new_columns]
    _custom = [key + sep + i for i in new_columns]
    return _cols + _custom


def _get_version_from_toml(path: str) -> str:
    """
    """
    with open(path, "r") as f:
        data = toml.loads(f.read())
        return data["tool"]["poetry"]["version"]
