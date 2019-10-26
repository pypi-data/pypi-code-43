import json
import csv
import os
from random import randint
from datetime import datetime


def open_json(path):
    """ untility function for opening json files """
    with open(path, 'r') as jsonfile:
        jsondata = json.load(jsonfile)
    return jsondata

def stringify(val):
    """ add string quotes and convert val to str """
    return "'{}'".format(val)

def get_random_val_from_list(ls):
    """ return a random element from a list """
    col_len = len(ls)
    index = randint(0, col_len-1)
    return ls[index]

def convert_date_to_timestamp(ds, ds_format, ts_format):
    """ convert datestamp to timestamp with ds_format and ts_format respectively """
    dsobj = datetime.strptime(ds, ds_format)
    ts = datetime.strftime(dsobj, ts_format)
    return ts

def get_time_diff(ts0, ts1, ts_format, units):
    ts0obj = datetime.strptime(ts0, ts_format)
    ts1obj = datetime.strptime(ts1, ts_format)
    diffobj = ts1obj - ts0obj
    if units == "days":
        delta = diffobj.days
    elif units == "seconds":
        days_delta = diffobj.days
        seconds_delta = diffobj.seconds
        delta = days_delta * 24 * 60 * 60 + seconds_delta
    else:
        raise ValueError("get_time_diff currently supports units == seconds or units == days. found {}".format(units))
    return delta

def get_default_file_name(table_name, ext):
    """ returns a default file path and name with extention ext """
    date = datetime.strftime(datetime.now(), '%Y-%m-%d')
    filename = "{table_name}.{date}.{ext}".format(
        table_name=table_name,
        date=date,
        ext=ext
    )
    return filename

def is_file(path):
    return os.path.isfile(path)

def is_contained_in_dir(path):
    dirname = os.path.dirname(path)
    return os.path.isdir(dirname)

def join_path_to_filename(path, filename):
    return os.path.join(path, filename)

def write_to_csv(path, dataset):
    """ write dataset to csv. dataset is a list of tuples """
    with open(path, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerows(dataset)
    csvfile.close()
    print("dataset has been written to csv file found at {}".format(path))

def write_to_text(path, dataset):
    """ write dataset to file located at path """
    with open(path, 'w') as outfile:
        outfile.write(dataset)
    outfile.close()
    print("dataset has been written to file found at {}".format(path))

def write_to_json(path, dataset):
    """ write dataset to json file located at path """
    with open(path, 'w', encoding='utf-8') as outfile:
        json.dump(dataset, outfile, ensure_ascii=False, indent=4)
    outfile.close()
    print("dataset has been written to json file found at {}".format(path))
