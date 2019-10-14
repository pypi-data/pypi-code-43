# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""US labor laus."""

from ._abstract_tabularopendataset import AbstractTabularOpenDataset
from .accessories.us_labor_laus_accessory import UsLaborLAUSAccessory
from azureml.data import TabularDataset


class UsLaborLAUS(AbstractTabularOpenDataset):
    """US labor laus class."""

    def __init__(
            self,
            dataset: TabularDataset = None,
            enable_telemetry: bool = True):
        """
        Initializes an instance of the UsLaborLAUS class.
        It can be initialized with or without dataset.

        :param dataset: if it's not None, then this will override all the arguments previously.
        :type dataset: Dataset
        :param enable_telemetry: whether to enable telemetry, disabled for UT only.
        :type enable_telemetry: bool
        """
        worker = UsLaborLAUSAccessory(enable_telemetry=enable_telemetry)
        if dataset is not None:
            worker.update_dataset(dataset, enable_telemetry=enable_telemetry)
            self.worker = worker
            TabularDataset.__init__(self)
            self._definition = dataset._definition
            self._properties = dataset._properties
        else:
            AbstractTabularOpenDataset.__init__(self, worker=worker)

    @staticmethod
    def get(dataset: TabularDataset, enable_telemetry: bool = True):
        """Get an instance of UsLaborLAUS.

        :param dataset: input an instance of TabularDataset.
        :type end_date: Dataset.
        :param enable_telemetry: whether to enable telemetry, disabled for UT only.
        :type enable_telemetry: bool
        :return: an instance of UsLaborLAUS.
        """
        pub = UsLaborLAUS(dataset=dataset, enable_telemetry=enable_telemetry)
        pub._tags = dataset.tags
        if enable_telemetry:
            AbstractTabularOpenDataset.log_get_operation(pub.worker)
        return pub
