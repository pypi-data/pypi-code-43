from . import DatabaseConnection
import dateutil.parser
import os
import csv
import time

try:
    import pandas as pd
    PANDAS_INSTALLED = True
except:
    PANDAS_INSTALLED = False

class DatabaseConnectionCSV(DatabaseConnection):
    """
    Class to define a DatabaseConnection to a CSV file
    """

    def __init__(
        self,
        path,
        time_series_database = True,
        object_database = True,
        data_field_names = None,
        convert_to_string_functions = {},
        convert_from_string_functions = {}
    ):
        """
        Constructor for DatabaseConnectionCSV.

        If the specified file exists, the method will check whether the header
        row of the file matches the specified field names (and raise an
        exception if it does not). If it does not exist, it will be created and
        a header row will be written.

        If time_series_database and object_database are both True, database is
        an object time series database (e.g., a measurement database) and
        datapoints are identified by timestamp and object ID. The fields
        'timestamp' and 'object_id' will be added automatically.

        If object_database is True and time_series_database is False, database
        is an object database (e.g., a device configuration database) and
        datapoints are identified by object ID. The field 'object_id' will be
        added automatically.

        If time_series_database is True and object_database is False, behavior
        is not defined (for now).

        The convert_to_string_functions and convert_from_string_functions
        arguments are dictionaries of functions to be used to convert values
        to/from strings when writing/reading to/from the CSV file. The keys are
        field names and the values are functions (typically lambda functions).
        If a field is not included, it will be converted to a string via the
        standard str() function when writing to the CSV file and it will be left
        as a string when reading from the CSV file. The exception is the
        'timestamp' field, which is converted to a string via the isoformat()
        method and converted from a string via dateutil.parser.parse().

        Parameters:
            path (string): Path to CSV file
            time_series_database (bool): Boolean indicating whether database is a time series database (default is True)
            object_database (bool): Boolean indicating whether database is an object database (default is True)
            data_field_names (list of string): Fields (other than 'timestamp' and 'object_id') to incude in CSV file
            convert_to_string_functions (dict of functions): Functions used to convert from values to strings
            convert_from_string_functions (dict of functions): Functions used to convert from strings to values
        """
        if not time_series_database and not object_database:
            raise ValueError('Database must be a time series database, an object database, or an object time series database')
        if data_field_names is not None and 'timestamp' in data_field_names:
            raise ValueError('Field name \'timestamp\' is reserved')
        if data_field_names is not None and 'object_id' in data_field_names:
            raise ValueError('Field name \'object_id\' is reserved')
        self.path = path
        self.time_series_database = time_series_database
        self.object_database = object_database
        self.convert_to_string_functions = convert_to_string_functions
        self.convert_from_string_functions = convert_from_string_functions
        if PANDAS_INSTALLED:
            self._fetch_data_object_time_series = self._fetch_data_object_time_series_pandas
            self._delete_data_object_time_series = self._delete_data_object_time_series_pandas
        else:
            self._fetch_data_object_time_series = self._fetch_data_object_time_series_python_native
            self._delete_data_object_time_series = self._delete_data_object_time_series_python_native
        self.field_names = []
        if time_series_database:
            self.field_names.append('timestamp')
        if object_database:
            self.field_names.append('object_id')
        if data_field_names is not None:
            self.field_names.extend(data_field_names)
        # Check if file already exists
        if os.path.exists(self.path):
            # If file already exists, check to see that header row of file matches
            # target field names
            with open(self.path, mode = 'r', newline = '') as fh:
                reader = csv.DictReader(fh)
                if reader.fieldnames != self.field_names:
                    raise Exception('Field names in file header ({}) do not match specified field names ({})'.format(
                        reader.fieldnames,
                        self.field_names
                    ))
        else:
            # If file does not exist, create it and write header row
            with open(self.path, mode = 'w', newline = '') as fh:
                writer = csv.DictWriter(fh, fieldnames = self.field_names)
                writer.writeheader()

    # Internal method for writing single datapoint of object time series data
    # (CSV-database-specific)
    def _write_datapoint_object_time_series(
        self,
        timestamp,
        object_id,
        data
    ):
        value_dict = {
            'timestamp': timestamp,
            'object_id': object_id
        }
        value_dict.update(data)
        string_dict = {field_name: self._convert_to_string(field_name, value_dict.get(field_name)) for field_name in self.field_names}
        with open(self.path, mode = 'a', newline = '') as fh:
            writer = csv.DictWriter(fh, self.field_names)
            writer.writerow(string_dict)

    # Internal method for writing multiple datapoints of object time series data
    # (CSV-database-specific)
    def _write_data_object_time_series(
        self,
        datapoints
    ):
        with open(self.path, mode = 'a', newline = '') as fh:
            writer = csv.DictWriter(fh, self.field_names)
            for datapoint in datapoints:
                string_dict = {field_name: self._convert_to_string(field_name, datapoint.get(field_name)) for field_name in self.field_names}
                writer.writerow(string_dict)

    # Native python version of internal method for fetching object time series
    # data (CSV-database-specific)
    def _fetch_data_object_time_series_python_native(
        self,
        start_time,
        end_time,
        object_ids
    ):
        fetched_data = []
        with open(self.path, mode = 'r', newline = '') as fh:
            reader = csv.DictReader(fh)
            string_dicts = list(reader)
            for string_dict in string_dicts:
                value_dict = {field_name: self._convert_from_string(field_name, string_dict.get(field_name)) for field_name in self.field_names}
                if start_time is not None and value_dict['timestamp'] < start_time:
                    continue
                if end_time is not None and value_dict['timestamp'] > end_time:
                    continue
                if object_ids is not None and value_dict['object_id'] not in object_ids:
                    continue
                fetched_data.append(value_dict)
        return fetched_data

    # Pandas version of internal method for fetching object time series data
    # (CSV-database-specific)
    def _fetch_data_object_time_series_pandas(
        self,
        start_time,
        end_time,
        object_ids
    ):
        converters = self.convert_from_string_functions
        df = pd.read_csv(
            self.path,
            parse_dates = ['timestamp'],
            infer_datetime_format = True,
            converters = converters,
            dtype = str
        )
        if len(df) == 0:
            return []
        if start_time is not None or end_time is not None or object_ids is not None:
            boolean = True
            if start_time is not None:
                boolean = boolean & (df['timestamp'] > start_time)
            if end_time is not None:
                boolean = boolean & (df['timestamp'] < end_time)
            if object_ids is not None:
                boolean = boolean & df['object_id'].isin(object_ids)
            df = df[boolean].reset_index(drop = True)
        fetched_data = df.to_dict('records')
        for i in range(len(fetched_data)):
            fetched_data[i]['timestamp'] = fetched_data[i]['timestamp'].to_pydatetime()
        return fetched_data

    # Native Python version of internal method for deleting object time series
    # data (CSV-database-specific)
    def _delete_data_object_time_series_python_native(
        self,
        start_time,
        end_time,
        object_ids
    ):
        read_fh = open(self.path, mode = 'r', newline = '')
        reader = csv.DictReader(read_fh)
        write_fh =  open('.temp.csv', 'w', newline = '')
        writer = csv.DictWriter(write_fh, fieldnames = self.field_names)
        writer.writeheader()
        for string_dict in reader:
            value_dict = {field_name: self._convert_from_string(field_name, string_dict.get(field_name)) for field_name in self.field_names}
            if value_dict['timestamp'] > start_time and value_dict['timestamp'] < end_time and value_dict['object_id'] in object_ids:
                continue
            writer.writerow(string_dict)
        write_fh.close()
        read_fh.close()
        time.sleep(1)
        os.replace('.temp.csv', self.path)

    # Pandas version of internal method for deleting object time series data
    # (CSV-database-specific)
    def _delete_data_object_time_series_pandas(
        self,
        start_time,
        end_time,
        object_ids
    ):
        converters = self.convert_from_string_functions
        df = pd.read_csv(
            self.path,
            parse_dates = ['timestamp'],
            infer_datetime_format = True,
            converters = converters,
            dtype = str
        )
        if len(df) == 0:
            return
        boolean = False
        boolean = boolean | (df['timestamp'] <= start_time)
        boolean = boolean | (df['timestamp'] >= end_time)
        boolean = boolean | ~(df['object_id'].isin(object_ids))
        df = df[boolean].reset_index(drop = True)
        for column_name in df.columns:
            if column_name == 'timestamp':
                continue
            elif column_name in self.convert_to_string_functions:
                df[column_name] = df[column_name].apply(self.convert_to_string_functions[column_name])
            else:
                df[column_name] = df[column_name].astype(str)
        df.to_csv(self.path, index = False)

    def _convert_from_string(self, field_name, string):
        if string is None or string == '':
            return None
        elif field_name in self.convert_from_string_functions.keys():
            return self.convert_from_string_functions[field_name](string)
        elif field_name == 'timestamp':
            return dateutil.parser.parse(string)
        else:
            return string

    def _convert_to_string(self, field_name, value):
        if value is None:
            return ''
        elif field_name in self.convert_to_string_functions.keys():
            return self.convert_to_string_functions[field_name](value)
        elif field_name == 'timestamp':
            return value.isoformat()
        else:
            return str(value)
