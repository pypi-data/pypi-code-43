from random import randint, random
from datetime import datetime, timedelta

from .common.Common import open_json, convert_date_to_timestamp, get_time_diff

from .common.paths import formats_path


""" expected datestamp and timestamp formats """
formats_json = open_json(formats_path)
common_ts_format = formats_json["common_ts_format"] # YYYY-mm-dd HH:MM:SS
common_ds_format = formats_json["common_ds_format"] # YYYY-mm-dd


""" Logic and untility functions for CodeGenerator classes """

def convert_common_ds_to_ts(ds):
    """ convert %Y-%m-%d to %Y-%m-%d %H:%M:%S """
    return convert_date_to_timestamp(ds, common_ds_format, common_ts_format)

def timestamp_add_seconds(ts, seconds):
    tsobj = datetime.strptime(ts, common_ts_format)
    tsobj = tsobj + timedelta(seconds=seconds)
    updated_ts = datetime.strftime(tsobj, common_ts_format)
    return updated_ts

def datestamp_add_days(ds, days):
    dsobj = datetime.strptime(ds, common_ds_format)
    dsobj = dsobj + timedelta(days=days)
    updated_ds = datetime.strftime(dsobj, common_ds_format)
    return updated_ds

def get_date_diff_days(ds0, ds1):
    ds0obj = datetime.strptime(ds0, common_ds_format)
    ds1obj = datetime.strptime(ds1, common_ds_format)
    return (ds1obj - ds0obj).days

def get_time_diff_seconds(ts0, ts1):
    delta = get_time_diff(ts0, ts1, common_ts_format, "seconds")
    return delta

def create_email(name1,  name2=None):
    digit = randint(2, 80)
    if name2:
        email = name1 + "." + name2
    else:
        email = name1
    email += str(digit) + "@fakeemail.com"
    return email

def get_name_columns(column_defs):
    """ return a list of column_name where is_name is True """
    output = []
    for column_name in column_defs:
        metadata = column_defs[column_name]
        is_name = metadata.get("is_name")
        if is_name:
            output.append(column_name)
    return output

def set_default_boundary_conditions(column_name, column_defs):
    """ returns default bounds for numeric, date or timestamp columns. For other
        columns lowerbnd, upperbnd will return the tuple None, None """
    lowerbnd, upperbnd = None, None
    metadata = column_defs[column_name]
    col_type = metadata.get("col_type")

    if col_type in {"int", "float"}:
        lowerbnd = 1
        upperbnd = 10
    elif col_type == "varchar":
        now_ = datetime.now()
        is_date = metadata.get("is_date")
        is_timestamp = metadata.get("is_timestamp")
        if is_date:
            lowerbnd = datetime.strftime(now_ + timedelta(days=-10), common_ds_format)
            upperbnd = datetime.strftime(now_, common_ds_format)
        elif is_timestamp:
            lowerbnd = datetime.strftime(now_ + timedelta(hours=-10), common_ts_format)
            upperbnd = datetime.strftime(now_, common_ts_format)

    return lowerbnd, upperbnd

def set_is_null(proportion_null=None):
    rand = random()
    is_null = rand < proportion_null if proportion_null else rand < 0.1
    return is_null

def get_val_from_fixed_map(fixed_map, row_values):
    column_name = fixed_map[0]
    key = row_values[column_name]
    mapping = fixed_map[1]
    val = mapping[key]
    return val

def set_float_val(lowerbnd, upperbnd):
    interval_len = upperbnd - lowerbnd
    val = round(random() * interval_len + lowerbnd, 2)
    return val
