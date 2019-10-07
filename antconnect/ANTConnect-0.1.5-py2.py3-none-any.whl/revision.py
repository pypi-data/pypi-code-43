from .api import API


class Revision:
    """Provides access to  properties and operations of a revision

    :param api: API layer
    :type api: API
    :param project_id: UUID of the project that this revision's table is member
        of
    :type project_id: str
    :param table_id: UUID of the table that this revision is member of
    :type table_id: str
    :param revision_details: revision details as provided by the CDE API
    :type revision_details: dict
    """
    _api = None
    _name = ''
    _project_id = ""
    _table_id = ""
    _revision_id = ""

    def __init__(self, api: API, project_id: str, table_id: str,
                 revision_details: dict):
        self._api = api
        self._name = revision_details["name"]
        self._project_id = project_id
        self._table_id = table_id
        self._revision_id = revision_details["id"]

    @staticmethod
    def from_uuids(api: API, project_id: str, table_id: str,
                   revision_id: str) -> 'Revision':
        """Creates a revision object from a project and table UUID

        :raises LookupError: Table does not exists
        :param project_id: UUID of the project that this revision's table is
            member of
        :type project_id: str
        :param table_id: UUID of the table that this revision is member of
        :type table_id: str
        :param revision_id: UUID of the revision
        :type revision_id: str
        :return: table object
        :rtype: Table
        """
        revision_details = api.revision_read(project_id, table_id, revision_id)

        if 'id' not in revision_details:
            raise SystemError("Revision does not exists")

        return Revision(api, project_id, table_id, revision_details)

    @property
    def name(self) -> str:
        """Identifying name of the table"""
        return self._name

    @name.setter
    def name(self, name: str):
        response = self._api.revision_update(
            self.project_id, self.table_id, self.revision_id, name)
        if 'id' not in response:
            raise ValueError(response["message"] if "message" in response
                             else "Could not update name")

        self._name = name

    @property
    def project_id(self) -> str:
        """UUID of the project that this revision's table is a member of"""
        return self._project_id

    @property
    def table_id(self) -> str:
        """UUID of the table that this revision is a member of"""
        return self._table_id

    @property
    def revision_id(self) -> str:
        """UUID of the revision"""
        return self._revision_id
