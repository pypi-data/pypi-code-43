#! usr/bin/env python3
#  -*- coding: utf-8 -*-

"""
**This module includes the following utils for input data management**

 It contains the following methods:
    - select_csv_file_between_dates() : select data in a .csv file
      between two dates
    - read_enedis_data_csv_file() : select and rearrange the data in a .csv
      file of Enedis (the French Distribion System Operator company),
      possibly between two dates

..
    Copyright 2018 G2Elab / MAGE

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

         http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import pandas as pd

__docformat__ = "restructuredtext en"


def select_csv_file_between_dates(file_path=None, start='DD/MM/YYYY HH:MM',
                                  end='DD/MM/YYYY HH:MM', v_cols=[],
                                  sep=';'):
    """
    Select data in a .csv file between two dates

    :param file_path: path of the file to rearrange
    :param start: DD MM YYYY HH:00 : first date which should be considered
    :param end: DD MM YYYY HH:00 : last date which should be considered
    :param v_cols: columns which should be considered
    :return: df: a dataframe considering the dates
    """

    # Read CSV file from path and store into dataframe df
    if not v_cols:
        df = pd.read_csv(file_path, sep=sep, usecols=[0, 1], header=0,
                         names=['date', 'value'])
    else:
        df = pd.read_csv(file_path, sep=sep, usecols=range(len(v_cols) + 1),
                         header=0, names=['date'] + v_cols)

    # Ensure that the 'date' column is at the format datetime
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)

    # Set the date as index
    df = df.set_index(['date'])
    df.sort_index()

    # Convert start and end into the format datetime
    start = pd.to_datetime(start, dayfirst=True)
    end = pd.to_datetime(end, dayfirst=True)

    # Select from start to end
    selected_df = df.loc[start: end]

    if not v_cols:
        return selected_df['value']
    else:
        return selected_df.loc[:, v_cols]


def read_enedis_data_csv_file(file_path=None, start=None, end=None):
    """
    Rearrange the Enedis data in cvs file in oder to have a Dataframe of the
    following form

    DD MM YYYY HH:00 ; a
    DD MM YYYY HH:30 ; b
    ...

    :param file_path: path of the file to rearrange
    :param start: DD MM YYYY HH:00 : first date which should be considered
    :param end: DD MM YYYY HH:00 : last date which should be considered
    :return: df_list: the data as a list
    """

    # read the cvs file and collect the data as DD MM YYYY HH:00 ; a ; b
    df_enedis = pd.read_csv(file_path, sep=';', usecols=[0, 1, 2],
                            names=['date', 'value', 'value_last_30min'])
    df_enedis.loc[:, 'date'] = pd.to_datetime(
        df_enedis.loc[:, 'date'], dayfirst=True)

    # Create a DataFrame with the data corresponding to the first 30 minutes
    df_first_30_min = df_enedis[['date', 'value']]

    # Create a DataFrame with the data corresponding to the last 30 minutes
    df_last_30_min = pd.DataFrame(
        {'date': pd.DatetimeIndex(df_enedis['date']) + pd.offsets.Minute(30),
         'value': df_enedis['value_last_30min'].values})

    # Merge both DataFrame and order
    df = pd.concat([df_first_30_min, df_last_30_min])
    # Ensure that the 'date' column is at the format datetime
    df.loc[:, 'date'] = pd.to_datetime(df.loc[:, 'date'], dayfirst=True)
    df = df.set_index(['date'])
    df = df.sort_index()

    if start and end:
        if isinstance(start, str) and isinstance(end, str):
            # Convert start and end into the format datetime
            start = pd.to_datetime(start, dayfirst=True)
            end = pd.to_datetime(end, dayfirst=True)
            # Select from start to end
            df = df.loc[start: end]
        else:
            raise TypeError("start and end values should be entered as string "
                            "'DD/MM/YYYY'")

    # TODO: enable to check the time
    # start = df.head(1).index.values[0]
    # end = df.tail(1).index.values[0]

    df = df['value'].values.tolist()

    return df
