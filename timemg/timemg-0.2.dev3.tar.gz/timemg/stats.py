# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import datetime


GOOD_UPPER_LIMIT = 9
GOOD_LOWER_LIMIT = 8   # 7.75
MEDIUM_UPPER_LIMIT = 10
MEDIUM_LOWER_LIMIT = 7


def make_datetime(date, time, day_init_hour=0):
    if time is not None:
        if time.hour < day_init_hour:
            date += datetime.timedelta(days=1)
        return datetime.datetime(date.year, date.month, date.day, time.hour, time.minute)
    else:
        return None


def make_dataframe(timemg_data):
    DATE_LABEL = 'Date'
    WAKE_UP_LABEL = 'Wake up'
    SLEEP_LABEL = 'Sleep'
    WORK_IN_LABEL = 'W. in'
    WORK_OUT_LABEL = 'W. out'

    date_index     = timemg_data.headers.index(DATE_LABEL)
    wake_up_index  = timemg_data.headers.index(WAKE_UP_LABEL)
    sleep_index    = timemg_data.headers.index(SLEEP_LABEL)
    work_in_index  = timemg_data.headers.index(WORK_IN_LABEL)
    work_out_index = timemg_data.headers.index(WORK_OUT_LABEL)

    date_list     = [timemg_data.get_data(record_index, date_index)     for record_index in range(timemg_data.num_rows)]
    wake_up_list  = [timemg_data.get_data(record_index, wake_up_index)  for record_index in range(timemg_data.num_rows)]
    sleep_list    = [timemg_data.get_data(record_index, sleep_index)    for record_index in range(timemg_data.num_rows)]
    work_in_list  = [timemg_data.get_data(record_index, work_in_index)  for record_index in range(timemg_data.num_rows)]
    work_out_list = [timemg_data.get_data(record_index, work_out_index) for record_index in range(timemg_data.num_rows)]

    data_list = [
                    [
                        make_datetime(record_date, wake_up_time),
                        make_datetime(record_date, sleep_time, day_init_hour=12),
                        make_datetime(record_date, work_in_time),
                        make_datetime(record_date, work_out_time)
                    ] for record_date, wake_up_time, sleep_time, work_in_time, work_out_time in zip(date_list, wake_up_list, sleep_list, work_in_list, work_out_list)
                ]

    df = pd.DataFrame(data_list, columns=("wakeup", "bedtime", "work_in", "work_out"), index=pd.to_datetime(date_list))

    # WUSHIFT #########################

    WAKE_UP_TIME_REFERENCE = '6 h 45 m 59 s'

    df["wushift"] = df.wakeup - df.index

    df["wushift"] = df.wushift - pd.Timedelta(WAKE_UP_TIME_REFERENCE)
    df["wushift"] = df.wushift.apply(lambda x: x.total_seconds() / 60.)  # Convert to float

    # BTSHIFT #########################

    BED_TIME_REFERENCE = '22 h 30 m 59 s'

    df["btshift"] = df.bedtime - df.index

    df["btshift"] = df.btshift - pd.Timedelta(BED_TIME_REFERENCE)
    df["btshift"] = df.btshift.apply(lambda x: x.total_seconds() / 60.)  # Convert to float

    # WISHIFT #########################

    WORK_IN_TIME_REFERENCE = '9 h 15 m 59 s'

    df["wishift"] = df.work_in - df.index

    df["wishift"] = df.wishift - pd.Timedelta(WORK_IN_TIME_REFERENCE)
    df["wishift"] = df.wishift.apply(lambda x: x.total_seconds() / 60.)  # Convert to float

    # WOSHIFT #########################

    WORK_OUT_TIME_REFERENCE = '18 h 30 m 59 s'

    df["woshift"] = df.work_out - df.index

    df["woshift"] = df.woshift - pd.Timedelta(WORK_OUT_TIME_REFERENCE)
    df["woshift"] = df.woshift.apply(lambda x: x.total_seconds() / 60.)  # Convert to float

    # WORK DURATION ###################

    df['work_duration'] = df.work_out - df.work_in

    df['work_duration_hrs'] = df.work_duration / np.timedelta64(1, 'h')

    # SLEEP DURATION ##################

    df['date'] = df.index

    # Detect whether 2 rows are not 2 consecutive days
    df['compute_sleep_duration'] = (df.date.diff() == pd.Timedelta('1 days'))

    # Compute sleep duration
    df['sleep_duration'] = df['wakeup'] - df['bedtime'].shift()

    # Put sleep duration to "NaT" when the previous row is not the previous day
    df.loc[~df.compute_sleep_duration, 'sleep_duration'] = pd.NaT

    df['sleep_duration_hrs'] = df.sleep_duration / np.timedelta64(1, 'h')

    # Categories

    df['sleep_duration_class'] = 'bad'
    df.loc[(df.sleep_duration_hrs >= GOOD_LOWER_LIMIT) & (df.sleep_duration_hrs <=  GOOD_UPPER_LIMIT), 'sleep_duration_class'] = 'good'
    df.loc[(df.sleep_duration_hrs >= MEDIUM_LOWER_LIMIT) & (df.sleep_duration_hrs <   GOOD_LOWER_LIMIT), 'sleep_duration_class'] = 'medium'
    df.loc[(df.sleep_duration_hrs  > GOOD_UPPER_LIMIT) & (df.sleep_duration_hrs <= MEDIUM_UPPER_LIMIT), 'sleep_duration_class'] = 'medium'

    ###################################

    df = df.sort_index()

    return df

