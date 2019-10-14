# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""US labor cpi."""

from ._abstract_tabularopendataset import AbstractTabularOpenDataset
from .accessories.us_labor_cpi_accessory import UsLaborCPIAccessory
from azureml.data import TabularDataset


class UsLaborCPI(AbstractTabularOpenDataset):
    """US labor cpi class."""

    def __init__(
            self,
            dataset: TabularDataset = None,
            enable_telemetry: bool = True):
        """
        Initializes an instance of the UsLaborCPI class.
        It can be initialized with or without dataset.

        :param dataset: if it's not None, then this will override all the arguments previously.
        :type dataset: Dataset
        :param enable_telemetry: whether to enable telemetry, disabled for UT only.
        :type enable_telemetry: bool
        """
        worker = UsLaborCPIAccessory(enable_telemetry=enable_telemetry)
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
        """Get an instance of UsLaborCPI.

        :param dataset: input an instance of TabularDataset.
        :type end_date: Dataset.
        :param enable_telemetry: whether to enable telemetry, disabled for UT only.
        :type enable_telemetry: bool
        :return: an instance of UsLaborCPI.
        """
        pub = UsLaborCPI(dataset=dataset, enable_telemetry=enable_telemetry)
        pub._tags = dataset.tags
        if enable_telemetry:
            AbstractTabularOpenDataset.log_get_operation(pub.worker)
        return pub
