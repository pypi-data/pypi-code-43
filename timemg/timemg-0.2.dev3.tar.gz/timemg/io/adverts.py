#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import json
import os

from timemg.data.adverts import AdvertsTable
from timemg.io.lock import lock_path, unlock_path

PY_DATE_FORMAT = "%Y-%m-%d"
PY_TIME_FORMAT = "%H:%M"

FILE_NAME = ".timemg.json"

ID_COLUMN_LABEL = "Date"

class AdvertsDataBase:

    def __init__(self):
        lock_path(self.path)


    def __del__(self):
        unlock_path(self.path)


    def load(self):
        """Load the JSON database."""

        json_data_dict = {}

        try:
            with open(self.path, "r") as fd:
                json_data_dict = json.load(fd)
        except FileNotFoundError:
            pass

        data = AdvertsTable()

        for advert_id, advert_dict in json_data_dict.items():
            advert_list = []

            for col_label, dtype in zip(data.headers, data.dtype):
                if col_label == ID_COLUMN_LABEL:
                    value = advert_id
                else:
                    if col_label in advert_dict:
                        value = advert_dict[col_label]
                    else:
                        value = None                   # TODO: None is not always the desired choice ?

                if value is not None:
                    if dtype == datetime.date:
                        value = datetime.datetime.strptime(value, PY_DATE_FORMAT).date()
                    elif dtype == datetime.time:
                        value = datetime.datetime.strptime(value, PY_TIME_FORMAT).time()

                advert_list.append(value)

            data.append(advert_list)

        return data


    def save(self, data):
        """Save the JSON database."""

        # Use a dict structure to have items sorted by ID automatically by the JSON parser (for some strange reason, the first and the last items are switched when a list is used)
        json_data_dict = {}

        for row_index in range(data.num_rows):
            advert_dict = {}

            for col_label, dtype, col_index in zip(data.headers, data.dtype, range(data.num_columns)):
                value = data.get_data(row_index=row_index, column_index=col_index)

                if value is not None:
                    if dtype == datetime.date:
                        value = value.strftime(format=PY_DATE_FORMAT)
                    elif dtype == datetime.time:
                        value = value.strftime(format=PY_TIME_FORMAT)

                    advert_dict[col_label] = value

            advert_id = advert_dict.pop(ID_COLUMN_LABEL)
            json_data_dict[advert_id] = advert_dict

        with open(self.path, "w") as fd:
            json.dump(json_data_dict, fd, sort_keys=True, indent=4)


    @property
    def path(self):
        home_path = os.path.expanduser("~")                 # TODO: does it work on Unix only ?
        file_path = os.path.join(home_path, FILE_NAME)
        return file_path
