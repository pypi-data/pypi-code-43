# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""US population by county."""

from ._abstract_tabularopendataset import AbstractTabularOpenDataset
from .accessories.us_population_county_accessory import UsPopulationCountyAccessory
from .dataaccess.dataset_partition_prep import prep_partition_year
from azureml.data import TabularDataset


class UsPopulationCounty(AbstractTabularOpenDataset):
    """US population by county class."""

    def __init__(
            self,
            dataset: TabularDataset = None,
            enable_telemetry: bool = True):
        """
        Initializes an instance of the UsPopulationCounty class.
        It can be initialized with or without dataset.

        :param dataset: if it's not None, then this will override all the arguments previously.
        :type dataset: Dataset
        :param enable_telemetry: whether to enable telemetry, disabled for UT only.
        :type enable_telemetry: bool
        """
        worker = UsPopulationCountyAccessory(enable_telemetry=enable_telemetry)
        if dataset is not None:
            worker.update_dataset(dataset, enable_telemetry=enable_telemetry)
            self.worker = worker
            TabularDataset.__init__(self)
            self._definition = dataset._definition
            self._properties = dataset._properties
        else:
            AbstractTabularOpenDataset.__init__(self, worker=worker, partition_prep_func=prep_partition_year)

    @staticmethod
    def get(dataset: TabularDataset, enable_telemetry: bool = True):
        """Get an instance of UsPopulationCounty.

        :param dataset: input an instance of TabularDataset.
        :type end_date: Dataset.
        :param enable_telemetry: whether to enable telemetry, disabled for UT only.
        :type enable_telemetry: bool
        :return: an instance of UsPopulationCounty.
        """
        pub = UsPopulationCounty(dataset=dataset, enable_telemetry=enable_telemetry)
        pub._tags = dataset.tags
        if enable_telemetry:
            AbstractTabularOpenDataset.log_get_operation(pub.worker)
        return pub
