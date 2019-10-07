from .api import API


class Record:
    """Provides access to  properties and operations of a record

    :param api: API layer
    :type api: API
    :param project_id: UUID of the project that this record's table is member
        of
    :type project_id: str
    :param table_id: UUID of the table that this record is member of
    :type table_id: str
    :param record_details: record details as provided by the CDE API
    :type record_details: dict
    """
    _api = None
    _project_id = ""
    _table_id = ""
    _record_id = ""

    def __init__(self, api: API, project_id: str, table_id: str,
                 record_details: dict):
        self._api = api
        self._project_id = project_id
        self._table_id = table_id
        self._record_id = record_details["id"]

        for key in record_details:
            if key != 'id':
                self.__dict__[key] = record_details[key]

        self.__dict__["_init"] = True

    @staticmethod
    def from_uuids(api: API,
                   project_id: str, table_id: str, record_id: str) -> 'Record':
        """Creates a record object from a project and table UUID

        :raises LookupError: Table does not exists
        :param project_id: UUID of the project that this record's table is
            member of
        :type project_id: str
        :param table_id: UUID of the table that this record is member of
        :type table_id: str
        :param record_id: UUID of the record
        :type record_id: str
        :return: table object
        :rtype: Table
        """
        record_details = api.record_read(project_id, table_id, record_id)

        if 'id' not in record_details:
            raise SystemError("Record does not exists")

        return Record(api, project_id, table_id, record_details)

    @property
    def project_id(self) -> str:
        """UUID of the project that this record's table is a member of"""
        return self._project_id

    @property
    def table_id(self) -> str:
        """UUID of the table that this record is a member of"""
        return self._table_id

    @property
    def record_id(self) -> str:
        """UUID of the record"""
        return self._record_id

    def __getattr__(self, name):
        if name not in self.__dict__:
            raise AttributeError("'Record' object has no attribute '{}'"
                                 .format(name))
        return self.__dict__["name"]

    def __setattr__(self, name, value):
        if "_init" not in self.__dict__:
            self.__dict__[name] = value
            return

        if name not in self.__dict__:
            raise AttributeError("'Record' object has no attribute '{}'"
                                 .format(name))

        response = self._api.record_update(self.project_id, self.table_id,
                                           self.record_id, {name: value})
        if 'id' not in response:
            raise ValueError(response["message"] if "message" in response
                             else "Could not update {}".format(name))
        self.__dict__[name] = value

    def update(self, values: dict) -> bool:
        """Updates multiple values of the record at once

        :param values: alues of the record. the keys are equal to the
            column names of the table
        :type values: dict
        :return: ``True`` on a successful update of the record
        :rtype: bool
        """
        response = self._api.record_update(self.project_id, self.table_id,
                                           self.record_id, values)
        if 'id' not in response:
            return False
        for key in values:
            if key != 'id':
                self.__dict__[key] = values[key]
        return True

    def history(self) -> dict:
        """T.B.D.

        :return: [description]
        :rtype: dict
        """
        return self._api.record_history(self.project_id, self.table_id,
                                        self.record_id)
