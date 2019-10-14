# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""US labor ehe national accessory."""

from .public_data import PublicData

from ..dataaccess._us_labor_ehe_national_blob_info import UsLaborEHENationalBlobInfo
from ..dataaccess.blob_parquet_descriptor import BlobParquetDescriptor
from ..dataaccess.pandas_data_load_limit import PandasDataLoadLimitNone


class UsLaborEHENationalAccessory(PublicData):
    """US labor ehe national accessory class."""

    _blobInfo = UsLaborEHENationalBlobInfo()

    data = BlobParquetDescriptor(_blobInfo)

    def __init__(
            self,
            enable_telemetry: bool = True):
        """
        Initialize accessory.

        :param enable_telemetry: whether to send telemetry
        :type enable_telemetry: bool
        """
        self.dataset = None
        self._registry_id = self._blobInfo.registry_id
        self.path = self._blobInfo.get_data_wasbs_path()

        super(UsLaborEHENationalAccessory, self).__init__(cols=None, enable_telemetry=enable_telemetry)
        if enable_telemetry:
            self.log_properties['Path'] = self.path

    def update_dataset(self, ds, enable_telemetry: bool = True):
        """Update dataset."""
        self.dataset = ds
        if enable_telemetry:
            self.log_properties['from_dataset'] = True

    def get_pandas_limit(self):
        """Get instance of pandas data load limit class."""
        return PandasDataLoadLimitNone()

    def _to_spark_dataframe(self, activity_logger):
        """To spark dataframe.

        :param activity_logger: activity logger

        :return: SPARK dataframe
        """
        descriptor = BlobParquetDescriptor(self._blobInfo)
        ds = descriptor.get_spark_dataframe(self)
        return ds

    def _to_pandas_dataframe(self, activity_logger):
        """
        Get pandas dataframe.

        :param activity_logger: activity logger

        :return: Pandas dataframe based on its own filters.
        :rtype: pandas.DataFrame
        """
        descriptor = BlobParquetDescriptor(self._blobInfo)
        ds = descriptor.get_pandas_dataframe(self)
        return ds
