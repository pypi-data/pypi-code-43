# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
#  This code is licensed under MIT license (see license.txt for details)

import logging
import json
from datetime import datetime
import os

logger = logging.getLogger('dativa.tools.athena_partition')

"""
A function that partitions and saves data in appropriate folders and sub folders
"""


def athena_partition(df, partition_categories, file_handler, suffix, columns_to_keep=None, name="",
                     partition_dtypes=None, date_time_format="%Y-%m-%d_%H%M%S.%f", partition_string="",
                     **kwargs):
    """

    :param df: The data frame to be partitioned
    :param partition_categories: The columns to partition the data on
    :param file_handler: The appropriate file handler to save the data, currently tested for dativa CSVHandler and
            ParquetHandler support, other handlers are untested
    :param suffix: The extension the file should be saved with, .csv for csv, and .parquet for parquet
    :param columns_to_keep: Columns to keep from the data frame, if not supplied default behaviour is to keep all
            columns
    :param date_time_format: To minimise chances of overwrite the saved files contain the date time of when this
            function was called, this param specifies the format of the date time
    :param name: If provided all files filename will start with this
    :param partition_string: Allows formatting folder names, will be dependant on how many partition categories there
            are, defaults to creating folders and sub folders in order of partitioning
    :param partition_dtypes: Can pass argument to set the dtype of a particular column, to ensure proper grouping, also
            doubles to checking the column doesnt contain values of an unexpected dtype
    :param kwargs: Any additional key word arguments to be passed to the handler
    :return: Returns a full list of all file paths created, doesnt return base path as part of this
    """

    if any(df[partition_categories].isna().any()) or any((df[partition_categories] == "").any()):
        raise ValueError('The partition columns contain NaN values')
    if not file_handler.base_path:
        raise ValueError('A base path must be specified within the File handler object')
    if columns_to_keep:
        for cols in columns_to_keep:
            if cols not in df.columns:
                raise IndexError("Not all columns from column keep are valid columns in the data frame")

    if partition_dtypes:
        part_dtype_dict = dict(zip(partition_categories, partition_dtypes))
        try:
            df = df.astype(part_dtype_dict)
        except ValueError:
            raise ValueError("Could not cast dtypes to column\n{}".format(part_dtype_dict))

    if not columns_to_keep:
        columns_to_keep = df.columns
    group_by_obj = df.groupby(partition_categories, sort=False)

    if not partition_string:
        for part_cat in partition_categories:
            partition_string = partition_string + "{}=".format(part_cat) + "{}/"

    paths = []
    for partition_values, group_df in group_by_obj:
        if len(partition_categories) > 1:
            path = partition_string.format(*partition_values)
        elif len(partition_categories) == 1:
            path = partition_string.format(partition_values)

        time = datetime.now().strftime(date_time_format)
        logger.info("time is {}".format(time))
        full_path = "{}{}{}".format(path, name, time + suffix) if name else "{}{}".format(path, time + suffix)
        msg = {"message": "Saving parquet to location {}".format(full_path)}
        logger.info(json.dumps(msg))
        paths.append(full_path)
        if file_handler.base_path.startswith("/"):
            try:
                os.makedirs("{}/{}".format(file_handler.base_path, full_path.rsplit("/", 1)[0]))
            except FileExistsError:
                pass
        file = "{}".format(full_path)
        file_handler.save_df(
            group_df[
                [col for col in df.columns if (col in columns_to_keep and col not in partition_categories)]],
            file, **kwargs)
    return paths
