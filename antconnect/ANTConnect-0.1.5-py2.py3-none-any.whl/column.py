from .api import API


class Column:
    """Provides access to  properties and operations of a column

    :param api: API layer
    :type api: API
    :param project_id: UUID of the project that the columns containing table is
        member of
    :type project_id: str
    :param column_details: column details as provided by the CDE API
    :type column_details: dict
    """

    _api = None
    _name = ''
    _project_id = ""
    _table_id = ""
    _column_id = ""

    def __init__(self, api: API, project_id: str, column_details: dict):
        self._api = api
        self._project_id = project_id
        self._table_id = column_details["table"]
        self._column_id = column_details["id"]
        self._name = column_details["name"]

    @staticmethod
    def from_uuids(api: API,
                   project_id: str, table_id: str, column_id: str) -> 'Column':
        """Creates a column object from a project, table and  UUID

        :raises LookupError: Table does not exists
        :param project_id: UUID of the project that this column's table is a
            member of
        :type project_id: str
        :param table_id: UUID of the table that this column is a member of
        :type table_id: str
        :param column_id: UUID of the column
        :type column_id: str
        :return: table object
        :rtype: Table
        """
        column_details = api.column_read(project_id, table_id, column_id)

        if 'id' not in column_details:
            raise SystemError("Column does not exists")

        return Column(api, project_id, column_details)

    @property
    def name(self) -> str:
        """Identifying name of the column"""
        return self._name

    @name.setter
    def name(self, name: str):
        response = self._api.column_update(
            self.project_id, self.table_id, self.column_id, name)
        if 'id' not in response:
            raise ValueError(response["message"] if "message" in response
                             else "Could not update name")
        self._name = name

    @property
    def project_id(self) -> str:
        """UUID of the project that this column's table is a member of"""
        return self._project_id

    @property
    def table_id(self) -> str:
        """UUID of the table that this column is a member of"""
        return self._table_id

    @property
    def column_id(self) -> str:
        """UUID of the column"""
        return self._column_id
