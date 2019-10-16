"""
.. module:: dh_at
   :platform: Unix, Windows
   :synopsis: A module which contains the common validations (range, nan etc)
   done on the data

.. moduleauthor:: Dharmateja Yarlagadda <dharmateja.yarlagadda@eneco.com>

"""

import os
import pyodbc
import logging
import settings
import pandas as pd
from retrying import retry
from datetime import datetime
import enecodhutils.database.dh_mssql as dh_mssql
from azure.storage.blob import BlockBlobService
from azure.storage.blob.baseblobservice import BaseBlobService
from azure.common import AzureMissingResourceHttpError

logging.basicConfig(format='%(asctime)s %(levelname)-4s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')


def no_previous_data_check(current_run_df, previous_run_df, datetime_col):
    """
    Check if the previous_df which is being sent is empty or not.
    If empty set check flag and return the updated raw_df
    :param current_run_df: The raw df from current run
    :param previous_run_df: The df containing previous run info.
    :param datetime_col: The column to use for merging.
    :return: The multiple run data and the da_with_no_previous boolean.
    """
    da_with_no_previous = False
    previous_run_df_local = previous_run_df.copy()
    if previous_run_df_local.empty:
        logging.info('DH_Utils: Day ahead data no previous entries.')
        multiple_run_data = current_run_df
        da_with_no_previous = True
    else:
        previous_run_df_local.columns = previous_run_df_local.columns.map(lambda x: str(x) + '_previous')
        if type(datetime_col) is list:
            right_on_col = []
            for col in datetime_col:
                right_on_col.append(col + '_previous')
        else:
            right_on_col = datetime_col + '_previous'
        multiple_run_data = current_run_df.merge(previous_run_df_local, left_on=datetime_col,
                                                 right_on=right_on_col,
                                                 how='inner')
    return multiple_run_data, da_with_no_previous


def retrieve_da_data(datasource):
    """
    retrieve DA data as current ID run is the first of the day.
    :param datasource: The datasource being used.
    :return: The previous_snapshot to compare and the boolean snapshot_exists
    """
    da_container_name = datasource[:-2].lower().replace('_', '') + 'davalidationsdata'
    blob_service = BaseBlobService(account_name=os.environ['KAFKA_FT_BLOB_ACCOUNT_NAME'],
                                   account_key=os.environ['KAFKA_FT_BLOB_ACCOUNT_KEY'])
    da_file_name = da_container_name + '.csv'
    blob_service.get_blob_to_path(da_container_name, da_file_name, da_file_name)
    snapshots_df = pd.read_csv(da_container_name + '.csv')
    previous_snapshot = snapshots_df[snapshots_df['snapshot'] == 1]
    os.remove(da_container_name + '.csv')
    return snapshots_df, previous_snapshot


def blob_check_and_update(datasource, current_snapshot, datetime_col='datetime'):
    """
    Check if the container for the given datasource exists with the corresponding blob.
    If yes return snapshot and also update the existing snapshot in container.
    :param datasource: The datasource being used.
    :param current_snapshot: The current snapshot data.
    :param datetime_col: The datetime column used to join the data.
    :return: The previous_snapshot to compare and the boolean snapshot_exists
    """
    container_name = datasource.lower().replace('_', '') + 'validationsdata'
    blob_service = BaseBlobService(account_name=os.environ['KAFKA_FT_BLOB_ACCOUNT_NAME'],
                                   account_key=os.environ['KAFKA_FT_BLOB_ACCOUNT_KEY'])
    block_blob_service = BlockBlobService(account_name=os.environ['KAFKA_FT_BLOB_ACCOUNT_NAME'],
                                          account_key=os.environ['KAFKA_FT_BLOB_ACCOUNT_KEY'])
    file_name = container_name + '.csv'
    previous_snapshot = pd.DataFrame
    snapshot_exists = False
    try:
        blob_service.list_blobs(container_name)
    except AzureMissingResourceHttpError:
        blob_service.create_container(container_name)
    if blob_service.exists(container_name, file_name):
        logging.info('DH_Utils: Loading data from previous snapshots.')
        blob_service.get_blob_to_path(container_name, file_name, container_name + '.csv')
        snapshots_df = pd.read_csv(container_name + '.csv')
        previous_snapshot = snapshots_df[snapshots_df['snapshot'] == 1]
        previous_snapshot_local = previous_snapshot.copy()
        if snapshots_df['snapshot'].min() == 1:
            snapshot_exists = True
        # Check if the previous snapshot and current snapshot have common data
        # To handle first few ID runs of the day.
        previous_snapshot_local.columns = previous_snapshot_local.columns.map(lambda x: str(x) + '_snapshots')
        previous_snapshot_local[datetime_col + '_snapshots'] = pd.to_datetime(
            previous_snapshot_local[datetime_col + '_snapshots'])
        multi_run_df = current_snapshot.merge(previous_snapshot_local, left_on=datetime_col,
                                              right_on=datetime_col + '_snapshots',
                                              how='inner')
        if multi_run_df.dropna().empty:
            current_time = datetime.utcnow()
            logging.info('DH_Utils: Loading data from previous DA snapshots.')
            # Check if first ID run of the day, hence empty.
            if current_time.hour == 0 and current_time.minute < 30:
                snapshots_df, previous_snapshot = retrieve_da_data(datasource)
        snapshots_df['snapshot'] = snapshots_df['snapshot'] - 1
        combined_df = pd.concat([snapshots_df[snapshots_df['snapshot'] > 0], current_snapshot])
        combined_df.to_csv(file_name, sep=',', index=False, date_format='%Y-%m-%d %H:%M:%S')
        blob_service.delete_blob(container_name, file_name)
        block_blob_service.create_blob_from_path(container_name, file_name, file_name)
        os.remove(file_name)
    else:
        current_snapshot.to_csv(file_name, sep=',', index=False, date_format='%Y-%m-%d %H:%M:%S')
        block_blob_service.create_blob_from_path(container_name, file_name, file_name)
    return previous_snapshot, snapshot_exists


def update_validated_flags(validated_df, column_name, check):
    """
    Check if the previous_df which is being sent is empty or not.
    If empty set check flag and return the updated raw_df
    :param validated_df: The df containing validated columns and previous flag values.
    :param column_name: The column for which the flag has to be updated.
    :param check: The type of check being performed.
    :return: validation flags updated dataframe
    """
    cond = (validated_df[column_name + '_' + check + '_flag'] == 1)
    validated_df.loc[cond, column_name + '_' + check + '_flag'] = validated_df.loc[
                                                                      cond, column_name + '_' + check + '_flag'] + \
                                                                  validated_df.loc[
                                                                      cond, column_name + '_' + check +
                                                                      '_flag_previous']
    validated_df.loc[cond, column_name] = validated_df.loc[cond, column_name + '_previous']
    return validated_df


def update_default_flags(df, columns_df, check):
    """
    Update the dataframe with the default flag values for the columns in the columns_df.
    :param df: The raw dataframe which has to be updated with the flags
    :param columns_df: The df containing the list of columns and their respective min/max thresholds.
    :param check: The type of check being performed.
    :return: default flags updated dataframe
    """
    col_to_check = check
    if check == 'range':
        col_to_check = 'min'
    for row in columns_df[columns_df[col_to_check].notnull()].itertuples():
        column_name = row.column_name
        df[column_name + '_' + check + '_flag'] = 0
    return df


@retry(stop_max_attempt_number=10, wait_fixed=500, retry_on_exception=dh_mssql.retry_if_error)
def get_columns_info(table_name, file_type='NA'):
    with pyodbc.connect('DRIVER={};SERVER={};DATABASE={};UID={};PWD={}'.format(
            settings.SQL_DRIVER, settings.SQL_HOST, settings.SQL_DATABASE, settings.SQL_USERNAME,
            settings.SQL_PASSWORD)) as db_connection_data:
        columns_info = pd.read_sql(
            "SELECT column_name,min_value, max_value, snapshot FROM ebal_validations_configurations WHERE table_name "
            " = '{}' and type = '{}'".format(table_name, file_type), con=db_connection_data)
    return columns_info


def null_check(raw_df, previous_run_df, columns_df, datetime_col='datetime'):
    """
    Validation rule to check if the given column has null values or not and add the corresponding flag variable.
    If there is a null replace with last known valid value .

    :param raw_df: The raw dataframe.
    :param previous_run_df: The dataframe corresponding to the previous run.
    :param columns_df: The df containing the list of columns.
    :param datetime_col: The datetime column which is used to join the data.
    :return: final dataframe with the value for null check
    """
    logging.info('DH_Utils: Started Null Check.')
    multiple_run_data, da_with_no_previous = no_previous_data_check(raw_df, previous_run_df, datetime_col)
    for row in columns_df.itertuples():
        column_name = row.column_name
        multiple_run_data[column_name + '_null_flag'] = (~multiple_run_data[column_name].notnull()) * 1
        if not da_with_no_previous:
            multiple_run_data = update_validated_flags(multiple_run_data, column_name, 'null')
    null_checked = multiple_run_data.loc[:, ~multiple_run_data.columns.str.endswith('_previous')]
    logging.info('DH_Utils: Finished Null Check.')
    return null_checked


def range_check(raw_df, previous_run_df, columns_df, datetime_col='datetime'):
    """
    Validation rule to check if the given column has values out of range and add the corresponding flag variable.
    If there is a value out of range replace with last known valid value

    :param raw_df: The raw dataframe.
    :param previous_run_df: The dataframe corresponding to the previous run.
    :param columns_df: The df containing the list of columns and their respective min/max thresholds.
    :param datetime_col: The datetime column which is used to join the data.
    :return: final dataframe with the value for range check
    """
    logging.info('DH_Utils: Started Range Check.')
    multiple_run_data, da_with_no_previous = no_previous_data_check(raw_df, previous_run_df, datetime_col)
    for row in columns_df[columns_df['min_value'].notnull()].itertuples():
        column_name = row.column_name
        min_value = row.min_value
        max_value = row.max_value
        multiple_run_data[column_name + '_range_flag'] = (~multiple_run_data[column_name].between(min_value, max_value,
                                                                                                  inclusive=True)) * 1
        if not da_with_no_previous:
            multiple_run_data = update_validated_flags(multiple_run_data, column_name, 'range')
    range_checked = multiple_run_data.loc[:, ~multiple_run_data.columns.str.endswith('_previous')]
    logging.info('DH_Utils: Finished Range Check.')
    return range_checked


def snapshot_check(raw_df, columns_df, previous_run_df, datasource, datetime_col='datetime', snapshot_number=5):
    """
    Validation rule to check if the given column has changed over time or not.
    If this check fails do not replace any values but raise a warning and critical mail.

    :param raw_df: The raw dataframe.
    :param columns_df: The df containing the list of columns and their respective min/max thresholds.
    :param previous_run_df: The df containing the previous run (validated) data.
    :param datasource: The datasource being checked. Raw source name to be appended with type (DA or ID) in lowercase.
    :param datetime_col: The datetime column which is used to join the data.
    :param snapshot_number: The no of snapshots to consider
    :return: final dataframe with the value for snapshot check
    """
    logging.info('DH_Utils: Started Snapshot Check.')
    multiple_run_data, da_with_no_previous = no_previous_data_check(raw_df, previous_run_df, datetime_col)
    current_snapshot = multiple_run_data.copy().loc[:,
                       ~raw_df.columns.str.endswith('_flag' or '_previous')]
    for row in columns_df[columns_df['snapshot'].notnull()].itertuples():
        snapshot_number = row.snapshot
    current_snapshot['snapshot'] = snapshot_number
    previous_snapshot, snapshot_exists = blob_check_and_update(datasource, current_snapshot, datetime_col)
    if (not da_with_no_previous) and snapshot_exists:
        previous_snapshot.columns = previous_snapshot.columns.map(lambda x: str(x) + '_snapshots')
        previous_snapshot[datetime_col + '_snapshots'] = pd.to_datetime(previous_snapshot[datetime_col + '_snapshots'])
        multiple_run_snapshot_combined_data = multiple_run_data.merge(previous_snapshot, left_on=datetime_col,
                                                                      right_on=datetime_col + '_snapshots',
                                                                      how='inner')
        for row in columns_df[columns_df['snapshot'].notnull()].itertuples():
            column_name = row.column_name
            multiple_run_snapshot_combined_data.round({column_name: 2, column_name + '_snapshots': 2})
            previous_snapshot_cond = \
                multiple_run_snapshot_combined_data[multiple_run_snapshot_combined_data['snapshot_snapshots'] == 1][
                    column_name + '_snapshots'].equals(multiple_run_snapshot_combined_data[
                                                           column_name])
            if previous_snapshot_cond:
                multiple_run_data[column_name + '_snapshot_flag'] = multiple_run_data[
                                                                        column_name + '_snapshot_flag_previous'] + 1
            else:
                multiple_run_data[column_name + '_snapshot_flag'] = 0
    else:
        update_default_flags(multiple_run_data, columns_df, 'snapshot')
    snapshot_checked = multiple_run_data.loc[:, ~multiple_run_data.columns.str.endswith('_previous')]
    logging.info('DH_Utils: Finished Snapshot Check.')
    return snapshot_checked
