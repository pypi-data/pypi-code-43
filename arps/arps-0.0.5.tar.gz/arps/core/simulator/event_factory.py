from arps.core.resources_table import ResourcesTable
from arps.core.simulator.estimators_table import EstimatorsTable


class EventFactory:

    def __init__(self,
                 resources_table: ResourcesTable = None,
                 estimators_table: EstimatorsTable = None) -> None:
        self.resources_table = resources_table
        self.estimators_table = estimators_table
