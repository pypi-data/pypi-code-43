from datetime import datetime

from .CodeGenLogic import get_name_columns

from .common.Common import open_json, is_contained_in_dir

from .common.paths import formats_path, parameters_path


""" expected datestamp and timestamp formats """
formats_json = open_json(formats_path)
common_ts_format = formats_json["common_ts_format"] # YYYY-mm-dd HH:MM:SS
common_ds_format = formats_json["common_ds_format"] # YYYY-mm-dd


""" Logic and utility funcitons for validating input parameters to DataGen class """

def validate_num_rows(num_rows):
    """ validate the num_rows SQLTableGen param. Return True if valid """
    condition1 = not isinstance(num_rows, int)
    condition2 = num_rows <= 0
    if condition1:
        raise TypeError("num_rows must by positive int but found type {}".format(type(num_rows)))
    elif condition2:
        raise ValueError("num_rows must be positive int but found {}".format(num_rows))
    return True

def validate_email(column_defs):
    column_names = get_name_columns(column_defs)
    if len(column_names) == 0:
        raise ValueError("must have an is_name column to use email")
    return True

def check_datestamp_format(ds, format):
    """ returns True if ds formatted to format else False """
    try:
        datetime.strptime(ds, format)
        return True
    except ValueError:
        return False
    except ex:
        print("found uncaught exception {}".format(ex))
        return False

def check_common_ds_format(ds):
    return check_datestamp_format(ds, common_ds_format)

def validate_ds_format(ds):
    if not check_common_ds_format(ds):
        raise ValueError("expected ds to have format YYYY-mm-dd but found {}".format(ds))
    return True

def check_timestamp_format(ts, format):
    """ returns True if ts formatted to format else False """
    try:
        datetime.strptime(ts, format)
        return True
    except ValueError:
        return False
    except ex:
        print("found uncaught exception {}".format(ex))
        return False

def check_common_ts_format(ts):
    return check_timestamp_format(ts, common_ts_format)

def validate_ts_format(ts):
    condition = check_common_ds_format(ts) or check_common_ts_format(ts)
    if not condition:
        raise ValueError("""expected timestamp input params to have format
            YYYY-mm-dd or YYYY-mm-dd HH:MM:SS""")
    return True

def get_metadata_types():
    parameters_json = open_json(parameters_path)
    parameter_types = parameters_json["parameter_type"]
    return parameter_types

def stringify_metadata_type(param, metadata_types):
    output = "<class "
    t = metadata_types[param]
    output += "'{}'>".format(t)
    return output

def validate_bounds(lowerbnd, upperbnd, is_date, is_timestamp):
    condition1 = isinstance(lowerbnd, int) and isinstance(upperbnd, str)
    condition2 = isinstance(lowerbnd, float) and isinstance(upperbnd, str)
    condition3 = isinstance(lowerbnd, str) and isinstance(upperbnd, int)
    condition4 = isinstance(lowerbnd, str) and isinstance(upperbnd, float)
    if condition1 or condition2 or condition3 or condition4:
        raise ValueError("expected lowerbnd and upperbnd to both be numeric or both be str. found lowerbnd: {lowerbnd} upperbnd: {upperbnd}".format(lowerbnd=lowerbnd, upperbnd=upperbnd))
    condition5 = lowerbnd > upperbnd
    if condition5:
        raise ValueError("expected lowerbnd <= upperbnd but found lowerbnd: {lowerbnd} upperbnd: {upperbnd}".format(lowerbnd=lowerbnd, upperbnd=upperbnd))
    if is_date:
        validate_ds_format(lowerbnd)
        validate_ds_format(upperbnd)
    if is_timestamp:
        validate_ts_format(lowerbnd)
        validate_ts_format(upperbnd)
    return True

def vaidate_fixed_collection(fixed_collection):
    condition = len(fixed_collection) == 0
    if condition:
        raise ValueError("fixed_collection should be non-empty")
    return True

def validate_fixed_map(fixed_map, column_defs):
    map_key = fixed_map[0]
    map_key_defs = column_defs.get(map_key)
    if not map_key_defs:
        raise KeyError("fixed_map should be associated to a defined column in this table but found None")

    map_values = fixed_map[1]
    if map_values is None:
        raise ValueError("fixed_map needs to have a dict object which associates value from {} but found None".format(map_key))
    if not isinstance(map_values, dict):
        raise TypeError("expected fixed_map values to be a dict object but found {}".format(type(map_values)))
    return True

def validate_nullable(column_name, is_nullable, proportion_null):
    if not is_nullable:
        raise ValueError("proportion_null defined for non nullable field {}. if intended to be nullable set is_nullable = True".format(column_name))

    condition1 = not (isinstance(proportion_null, int) or isinstance(proportion_null, float))
    if condition1:
        raise ValueError("proportion_null must be numeric value. found {}".format(proportion_null))

    condition2 = proportion_null < 0 or proportion_null > 1
    if condition2:
        raise ValueError("proportion_null must be a value between 0 and 1. found {}".format(proportion_null))
    return True

def validate_column_defs(column_name, column_defs):
    """ validate the column_defs param. Return True if valid """
    metadata = column_defs.get(column_name)
    if not metadata:
        raise KeyError("not column named {} found in column_defs".format(column_name))

    col_type = metadata.get("col_type") # int, float, varchar, bool
    if col_type not in {"int", "float", "varchar", "bool"}:
        raise ValueError("col_type expected one of: int, float, varhcar, bool but found {}".format(col_type))

    is_primary_key = metadata.get("is_primary_key")
    if is_primary_key and col_type != "int":
        raise ValueError("primary key column is expected to be of type int. found {}".format(col_type))

    is_email = metadata.get("is_email")
    if is_email:
        validate_email(column_defs)

    is_date = metadata.get("is_date")
    is_timestamp = metadata.get("is_timestamp")

    bounds = metadata.get("bounds")
    if bounds:
        lowerbnd = bounds[0]
        upperbnd = bounds[1]
        validate_bounds(lowerbnd, upperbnd, is_date, is_timestamp)

    fixed_collection = metadata.get("fixed_collection")
    if fixed_collection is not None:
        vaidate_fixed_collection(fixed_collection)

    fixed_map = metadata.get("fixed_map")
    if fixed_map is not None:
        validate_fixed_map(fixed_map, column_defs)

    is_nullable = metadata.get("is_nullable")

    if is_primary_key and is_nullable:
        raise ValueError("primary key can not be nullable")

    proportion_null = metadata.get("proportion_null")
    if proportion_null is not None:
        validate_nullable(column_name, is_nullable, proportion_null)

    return True

def validate_metadata_type(column_defs, column_name, param):
    error_msg = """found mismatched types for column name: {column_name}.
        expected {expected_type} but found {found_type}."""

    metadata_types = get_metadata_types()
    expected_type = stringify_metadata_type(param, metadata_types)

    column_def = column_defs[column_name]
    param_def = column_def.get(param)
    found_type = type(param_def)

    if expected_type != str(found_type):
        raise ValueError(error_msg.format(
            column_name=column_name,
            expected_type=expected_type,
            found_type=found_type
            )
        )
    return True

def validate_metadata_types(column_defs):
    for column_name in column_defs:
        metadata = column_defs[column_name]
        for param in metadata:
            validate_metadata_type(column_defs, column_name, param)
    return True

def validate_varchar_length(column_defs, column_name):
    """ validation for varchar_length parameter """
    return

def validate_path(path):
    """ validation for the DataGen path parameter """
    isdir = is_contained_in_dir(path)
    if not isdir:
        raise ValueError("found invalid path: {}".format(path))
    return True
