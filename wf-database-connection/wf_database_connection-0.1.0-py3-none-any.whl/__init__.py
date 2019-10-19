import datetime
import dateutil.parser

class DatabaseConnection:
    """
    Class to define a simple, generic database interface that can be adapted to
    different use cases and implementations.

    All methods must be implemented by derived classes.
    """

    def write_datapoint_object_time_series(
        self,
        timestamp,
        object_id,
        data
    ):
        """
        Write a single datapoint for a given timestamp and object ID.

        Timestamp must either be a native Python datetime or a string which is
        parsable by dateutil.parser.parse(). If timestamp is timezone-naive,
        timezone is assumed to be UTC.

        Data must be serializable by native Python json methods.

        Parameters:
            timestamp (datetime or string): Timestamp associated with data
            object_id (string): Object ID associated with data
            data (dict): Data to be written
        """
        if not self.time_series_database or not self.object_database:
            raise ValueError('Writing datapoint by timestamp and object ID only enabled for object time series databases')
        timestamp = self._python_datetime_utc(timestamp)
        return_value = self._write_datapoint_object_time_series(
            timestamp,
            object_id,
            data
        )
        return return_value

    def write_data_object_time_series(
        self,
        datapoints
    ):
        """
        Write multiple datapoints with timestamps and object IDs.

        Input should be a list of dicts. Each dict must contain a 'timestamp'
        element and an 'object_id' element.

        Timestamps must either be native Python datetimes or strings which are
        parsable by dateutil.parser.parse(). If timestamp is timezone-naive,
        timezone is assumed to be UTC.

        Data must be serializable by native Python json methods.

        Parameters:
            datapoints (list of dict): Datapoints to be written
        """
        if not self.time_series_database or not self.object_database:
            raise ValueError('Writing datapoint by timestamp and object ID only enabled for object time series databases')
        parsed_datapoints = []
        for datapoint in datapoints:
            if 'timestamp' not in datapoint.keys():
                raise ValueError('Each datapoint must contain a timestamp')
            if 'object_id' not in datapoint.keys():
                raise ValueError('Each datapoint must contain an object ID')
            datapoint['timestamp'] = self._python_datetime_utc(datapoint['timestamp'])
            parsed_datapoints.append(datapoint)
        return_value = self._write_data_object_time_series(
            parsed_datapoints
        )
        return return_value

    def fetch_data_object_time_series(
        self,
        start_time = None,
        end_time = None,
        object_ids = None
    ):
        """
        Fetch data for a given timespan and set of object IDs.

        If specified, start time and end time must either be native Python
        datetimes or strings which are parsable by dateutil.parser.parse(). If
        they are timezone-naive, they are assumed to be UTC.

        If start time is not specified, all data is returned back to earliest
        data in database. If end time is not specified, all data is returned up
        to most recent data in database. If object IDs are not specified, data
        is returned for all objects.

        Returns a list of dictionaries, one for each datapoint.

        Parameters:
            start_time (datetime or string): Beginning of timespan (default: None)
            end_time (datetime or string): End of timespan (default: None)
            object_ids (list of strings): Object IDs (default: None)

        Returns:
            (list of dict): All data associated with specified time span and object IDs
        """
        if not self.time_series_database or not self.object_database:
            raise ValueError('Fetching data by time interval and/or object ID only enabled for object time series databases')
        if start_time is not None:
            start_time = self._python_datetime_utc(start_time)
        if end_time is not None:
            end_time = self._python_datetime_utc(end_time)
        data = self._fetch_data_object_time_series(
            start_time,
            end_time,
            object_ids
        )
        return data

    def delete_data_object_time_series(
        self,
        start_time,
        end_time,
        object_ids
    ):
        """
        Delete data for a given timespan and set of object IDs.

        Start time, end time, and object IDs must all be specified.

        Start time and end time must either be native Python datetimes or
        strings which are parsable by dateutil.parser.parse(). If they are
        timezone-naive, they are assumed to be UTC.

        Parameters:
            start_time (datetime or string): Beginning of timespan
            end_time (datetime or string): End of timespan
            object_ids (list of strings): Object IDs
        """
        if not self.time_series_database or not self.object_database:
            raise ValueError('Deleting data by time interval and/or object ID only enabled for object time series databases')
        if start_time is None:
            raise ValueError('Start time must be specified for delete data operation')
        if end_time is None:
            raise ValueError('End time must be specified for delete data operation')
        if object_ids is None:
            raise ValueError('Object IDs must be specified for delete data operation')
        start_time = self._python_datetime_utc(start_time)
        end_time = self._python_datetime_utc(end_time)
        self._delete_data_object_time_series(
            start_time,
            end_time,
            object_ids
        )

    def to_data_queue(
        self,
        start_time = None,
        end_time = None,
        object_ids = None
    ):
        """
        Create an iterable which returns datapoints from the database in time order.

        If specified, start time and end time must either be native Python
        datetimes or strings which are parsable by dateutil.parser.parse(). If
        they are timezone-naive, they are assumed to be UTC.

        If start time is not specified, all data is returned back to earliest
        data in database. If end time is not specified, all data is returned up
        to most recent data in database. If object IDs are not specified, data
        is returned for all objects.

        Returns a DataQueue object which contains the requested data.

        Parameters:
            start_time (datetime or string): Beginning of timespan (default: None)
            end_time (datetime or string): End of timespan (default: None)
            object_ids (list of strings): Object IDs (default: None)

        Returns:
            (DataQueue): Iterator which contains the requested data
        """
        data = self.fetch_data_object_time_series(
            start_time,
            end_time,
            object_ids
        )
        data_queue = DataQueue(
            data = data
        )
        return data_queue

    def _python_datetime_utc(self, timestamp):
        try:
            if timestamp.tzinfo is None:
                datetime_utc = timestamp.replace(tzinfo = datetime.timezone.utc)
            else:
                datetime_utc = timestamp.astimezone(tz=datetime.timezone.utc)
        except:
            datetime_parsed = dateutil.parser.parse(timestamp)
            if datetime_parsed.tzinfo is None:
                datetime_utc = datetime_parsed.replace(tzinfo = datetime.timezone.utc)
            else:
                datetime_utc = datetime_parsed.astimezone(tz=datetime.timezone.utc)
        return datetime_utc

    def _write_datapoint_object_time_series(
        self,
        timestamp,
        object_id,
        data
    ):
        raise NotImplementedError('Specifics of communication with database must be implemented in child class')

    def _write_data_object_time_series(
        self,
        datapoints
    ):
        raise NotImplementedError('Specifics of communication with database must be implemented in child class')

    def _fetch_data_object_time_series(
        self,
        start_time,
        end_time,
        object_ids
    ):
        raise NotImplementedError('Specifics of communication with database must be implemented in child class')

    def _delete_data_object_time_series(
        self,
        start_time,
        end_time,
        object_ids
    ):
        raise NotImplementedError('Specifics of communication with database must be implemented in child class')

class DataQueue:
    """
    Class to define an iterable which returns datapoints in time order.
    """
    def __init__(
        self,
        data
        ):
        """
        Constructor for DataQueue.

        Data must be in the format returned by
        DatabaseConnection.fetch_data_object_time_series() (i.e., simple list of
        dicts containing the datapoints; every datapoint must contain a
        'timestamp' field in timezone-aware native Python datetime format).

        Parameters:
            data (list of dict): Data to populate the queue
        """
        data.sort(key = lambda datapoint: datapoint['timestamp'])
        self.data = data
        self.num_datapoints = len(data)
        self.next_data_pointer = 0

    def __iter__(self):
        return self

    def __next__(self):
        """
        Fetch datapoint associated with the next timestamp.

        Data will be fetched in time order.

        Returns:
            (dict): Data associated with the next timestamp
        """
        if self.next_data_pointer >= self.num_datapoints:
            raise StopIteration()
        else:
            datapoint = self.data[self.next_data_pointer]
            self.next_data_pointer += 1
            return datapoint
