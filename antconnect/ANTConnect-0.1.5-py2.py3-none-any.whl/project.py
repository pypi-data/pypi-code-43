from .api import API
from .table import Table


class Project:
    """Provides access to  properties and operations of a project

    :param api: API layer
    :type api: API
    :param project_details: project details as provided by the CDE API
    :type project_details: dict
    """

    _api = None
    _name = ''
    _project_id = ''

    def __init__(self, api: API, project_details: dict):
        self._api = api
        self._name = project_details["name"]
        self._project_id = project_details["id"]

    @staticmethod
    def from_uuid(api: API, project_id: str) -> 'Project':
        """Creates a project object from a project UUID

        :raises LookupError: Project does not exists
        :param project_id: UUID of the project
        :type project_id: str
        :return: project object
        :rtype: Project
        """
        project_details = api.project_read(project_id)

        if 'id' not in project_details:
            raise LookupError("Project does not exists")

        return Project(api, project_details)

    @property
    def project_id(self) -> str:
        """UUID of the project"""
        return self._project_id

    @property
    def name(self) -> str:
        """Identifying name of the project"""
        return self._name

    @name.setter
    def name(self, name: str):
        response = self._api.project_update(self.project_id, name)
        if 'id' not in response:
            raise ValueError(response["message"] if "message" in response
                             else "Could not update name")

        self._name = name

    def tables(self):
        """Generator providing all the tables in the project"""
        tables = self._api.tables_read(self.project_id)
        for table in tables:
            yield Table(self._api, table_details=table)

    def all_tables(self) -> [Table]:
        """Fetches all tables of the project

        :return: List of tables
        :rtype: [Table]
        """
        return [table for table in self.tables()]

    def table(self, name: str) -> Table:
        """Looks up a table by *name*

        Note: when there are multiple tables with the same *name* the first
        match will be returned.

        :param name: name of the requested table
        :type name: str
        :raises LookupError: Table *name* not found
        :return: object of the requested table
        :rtype: Table
        """
        for table in self.tables():
            if table.name == name:
                return table

        raise LookupError("Table '{}' not found".format(name))

    def table_by_uuid(self, table_id: str) -> Table:
        """Fetches a Table by its UUID

        :param table_id: UUID of the table
        :type table_id: str
        :return: object of the requested table
        :rtype: Table
        """
        return Table.from_uuids(self._api, self.project_id, table_id)

    def add_table(self, name: str) -> bool:
        """Add a table to the project with a given name

        :param name: name of the table
        :type name: str
        :return: ``True`` when the table was added succesfully
        :rtype: bool
        """
        response = self._api.table_create(self.project_id, name)
        return 'id' in response

    def remove_table(self, table: Table) -> bool:
        """Removes a table from the project

        :param table: table object of the table that is to be removed
        :type table: Table
        :return: ``True`` when the table was succesfully removed
        :rtype: bool
        """
        response = self._api.table_delete(self.project_id, table.table_id)
        return 'message' in response \
            and response["message"] == "Resource deleted successfully"
