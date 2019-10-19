from . import DatabaseConnection

class DatabaseConnectionMemory(DatabaseConnection):
    """
    Class to define a DatabaseConnection to a database in memory
    """

    def __init__(
        self,
        time_series_database = True,
        object_database = True
    ):
        """
        Constructor for DatabaseConnectionMemory.

        If time_series_database and object_database are both True, database is
        an object time series database (e.g., a measurement database) and
        datapoints are identified by timestamp and object ID.

        If object_database is True and time_series_database is False, database
        is an object database (e.g., a device configuration database) and
        datapoints are identified by object ID.

        If time_series_database is True and object_database is False, behavior
        is not defined (for now).

        Parameters:
            time_series_database (bool): Boolean indicating whether database is a time series database (default is True)
            object_database (bool): Boolean indicating whether database is an object database (default is True)
        """
        if not time_series_database and not object_database:
            raise ValueError('Database must be a time series database, an object database, or an object time series database')
        self.time_series_database = time_series_database
        self.object_database = object_database
        self.data = []

    # Internal method for writing single datapoint of object time series data
    # (memory-database-specific)
    def _write_datapoint_object_time_series(
        self,
        timestamp,
        object_id,
        data
    ):
        datum = {
            'timestamp': timestamp,
            'object_id': object_id
        }
        datum.update(data)
        self.data.append(datum)

    # Internal method for writing multiple datapoints of object time series data
    # (memory-database-specific)
    def _write_data_object_time_series(
        self,
        datapoints
    ):
        self.data.extend(datapoints)

    # Internal method for fetching object time series data (memory-database-specific)
    def _fetch_data_object_time_series(
        self,
        start_time,
        end_time,
        object_ids
    ):
        fetched_data = []
        for datum in self.data:
            if start_time is not None and datum['timestamp'] < start_time:
                continue
            if end_time is not None and datum['timestamp'] > end_time:
                continue
            if object_ids is not None and datum['object_id'] not in object_ids:
                continue
            fetched_data.append(datum)
        return fetched_data

    # Internal method for deleting object time series data (memory-database-specific)
    def _delete_data_object_time_series(
        self,
        start_time,
        end_time,
        object_ids
    ):
        for i in range(len(self.data) - 1, -1, -1):
            if self.data[i]['timestamp'] < start_time:
                continue
            if self.data[i]['timestamp'] > end_time:
                continue
            if self.data[i]['object_id'] not in object_ids:
                continue
            del self.data[i]
