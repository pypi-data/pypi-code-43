# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""New York City safety."""

from datetime import datetime
from ._abstract_tabularopendataset import AbstractTabularOpenDataset
from .accessories.nyc_safety_accessory import NycSafetyAccessory
from azureml.data import TabularDataset
from typing import List, Optional


class NycSafety(AbstractTabularOpenDataset):
    """New York city safety class."""

    def __init__(
            self,
            start_date: datetime = NycSafetyAccessory.default_start_date,
            end_date: datetime = NycSafetyAccessory.default_end_date,
            cols: Optional[List[str]] = None,
            dataset: TabularDataset = None,
            enable_telemetry: bool = True):
        """
        Initializes an instance of the NycSafety class.
        It can be initialized from parameters, or dataset alone, but can't from both.

        :param start_date: start date you'd like to query inclusively.
        :type start_date: datetime
        :param end_date: end date you'd like to query inclusively.
        :type end_date: datetime
        :param cols: a list of column names you'd like to retrieve. None will get all columns.
        :type cols: List[str]
        :param dataset: if it's not None, then this will override all the arguments previously.
        :type dataset: Dataset
        :param enable_telemetry: whether to enable telemetry, disabled for UT only.
        :type enable_telemetry: bool
        """
        worker = NycSafetyAccessory(
            start_date=start_date,
            end_date=end_date,
            cols=cols,
            enable_telemetry=enable_telemetry)
        if dataset is not None:
            if start_date != NycSafetyAccessory.default_start_date and \
                end_date != NycSafetyAccessory.default_end_date and \
                    cols is not None:
                raise ValueError('With enable_telemetry excluded, it is invalid to set dataset and other parameters \
at the same time! Please use either of them.')
            worker.update_dataset(dataset, enable_telemetry=enable_telemetry)
            self.worker = worker
            TabularDataset.__init__(self)
            self._definition = dataset._definition
            self._properties = dataset._properties
        else:
            AbstractTabularOpenDataset.__init__(self, worker=worker, fine_grain_timestamp='datetime')

    @staticmethod
    def get(dataset: TabularDataset, enable_telemetry: bool = True):
        """Get an instance of NycSafety.

        :param dataset: input an instance of TabularDataset.
        :type end_date: Dataset.
        :param enable_telemetry: whether to enable telemetry, disabled for UT only.
        :type enable_telemetry: bool
        :return: an instance of NycSafety.
        """
        nyc = NycSafety(dataset=dataset, enable_telemetry=enable_telemetry)
        nyc._tags = dataset.tags
        if enable_telemetry:
            AbstractTabularOpenDataset.log_get_operation(nyc.worker)
        return nyc
