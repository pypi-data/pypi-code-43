from .column import Column
from .revision import Revision
from .record import Record
from .api import API


class Table:
    """Provides access to  properties and operations of a table

    :param api: API layer
    :type api: API
    :param table_details: table details as provided by the CDE API
    :type table_details: dict
    """
    _api = None
    _name = ''
    _project_id = ""
    _table_id = ""

    def __init__(self, api: API, table_details: dict):
        self._api = api
        self._name = table_details["name"]
        self._project_id = table_details["project"]
        self._table_id = table_details["id"]

    @staticmethod
    def from_uuids(api: API, project_id: str, table_id: str) -> 'Table':
        """Creates a table object from a project and table UUID

        :raises LookupError: Table does not exists
        :param project_id: UUID of the project that this table is member of
        :type project_id: str
        :param project_id: UUID of the table
        :type project_id: str
        :return: table object
        :rtype: Table
        """
        table_details = api.table_read(project_id, table_id)

        if 'id' not in table_details:
            raise SystemError("Table does not exists")

        return Table(api, table_details)

    @property
    def name(self) -> str:
        """Identifying name of the table"""
        return self._name

    @name.setter
    def name(self, name: str):
        response = self._api.table_update(self.project_id, self.table_id, name)
        if 'id' not in response:
            raise ValueError(response["message"] if "message" in response
                             else "Could not update name")

        self._name = name

    @property
    def project_id(self) -> str:
        """UUID of the project that this table is a member of"""
        return self._project_id

    @property
    def table_id(self) -> str:
        """UUID of the table"""
        return self._table_id

    def columns(self):
        """Generator providing all the columns in the table"""
        columns = self._api.columns_read(self.project_id, self.table_id)
        for column_details in columns:
            yield Column(self._api, self.project_id, column_details)

    def all_columns(self) -> [Column]:
        """Fetches all columns of the table

        :return: List of columns
        :rtype: [Column]
        """
        return [column for column in self.columns()]

    def column(self, name: str) -> Column:
        """Looks up a column by *name*

        Note: when there are multiple columns with the same *name* the first
        match will be returned.

        :param name: name of the requested column
        :type name: str
        :raises LookupError: Column *name* not found
        :return: object of the requested column
        :rtype: Table
        """
        for column in self.columns():
            if column.name == name:
                return column

        raise LookupError("Column '{}' not found".format(name))

    def column_by_uuid(self, column_id: str) -> Column:
        """Fetches a Column by its UUID

        :param column_id: UUID of the table
        :type column_id: str
        :return: object of the requested column
        :rtype: Column
        """
        return Column.from_uuids(self._api,
                                 self.project_id, self.table_id, column_id)

    def add_column(self, name: str, fieldtype: str, default_value: str = "",
                   options: [str] = None) -> bool:
        """Add a column to the table with a given name

        :param name: name of the column
        :type name: str
        :return: ``True`` when the column was added succesfully
        :rtype: bool
        """
        options = [] if options is None else options
        response = self._api.column_create(
            self.project_id, self.table_id,
            name, fieldtype, options, default_value)
        return 'id' in response

    def remove_column(self, column: Column) -> bool:
        """Removes a column from the project

        :param column: column object of the table that is to be removed
        :type column: Column
        :return: ``True`` when the column was succesfully removed
        :rtype: bool
        """
        response = self._api.column_delete(
            self.project_id, self.table_id, column.column_id)
        return 'message' in response \
            and response["message"] == "Resource deleted successfully"

    def records(self):
        """Generator providing all the records in the project"""
        records = self._api.records_read(self.project_id, self.table_id)
        for record in records:
            yield Record(self._api,
                         self.project_id, self.table_id, record_details=record)

    def all_records(self) -> [Record]:
        """Fetches all records of the table

        :return: List of records
        :rtype: [Record]
        """
        return [record for record in self.records()]

    def import_records(self, records_csv: str) -> bool:
        """import multiple records into the table at once

        :param records_csv: comma seperated values **mark up to be determined**
        :type records_csv: str
        :return: ``True on successfull import``
        :rtype: bool
        """
        self._api.records_create(self.project_id, self.table_id, records_csv)
        return None

    def remove_records(self, records: [Record]) -> bool:
        """Remove multiple records from the table at once

        :param records: List of the records that are to be removed
        :type records: [Record]
        :return: ``True`` on a successful removal process
        :rtype: bool
        """
        records_ids = [record.record_id for record in records]
        response = self._api.records_delete(
            self.project_id, self.table_id, records_ids)

        return ("message" in response
                and response["message"] == "Records deleted successfully")

    def verify_records(self, records_csv: str) -> bool:
        """To be determined

        :param records_csv:  comma seperated values **mark up to be
            determined**
        :type records_csv: str
        :return: ``True`` on successful validation
        :rtype: bool
        """
        self._api.records_verify(self.project_id, self.table_id, records_csv)
        return None

    def record_by_uuid(self, record_id: str) -> Record:
        """Fetches a Record by its UUID

        :param record_id: UUID of the record
        :type record_id: str
        :return: object of the requested record
        :rtype: Record
        """
        return Record.from_uuids(self._api,
                                 self.project_id, self.table_id, record_id)

    def add_record(self, record_values: dict) -> bool:
        """Add a record to the table

        :param record_values: values of the record. the keys are equal to the
            column names of the table
        :type name: dict
        :return: ``True`` when the record was added succesfully
        :rtype: bool
        """
        response = self._api.record_create(
            self.project_id, self.table_id, record_values)
        return 'id' in response

    def remove_record(self, record: Record) -> bool:
        """Removes a record from the table

        Note when multiple records are to be removed use ``remove_records()``

        :param record: record object of the record that is to be removed
        :type table: Record
        :return: ``True`` when the record was succesfully removed
        :rtype: bool
        """
        response = self._api.record_delete(
            self.project_id, self.table_id, record.record_id)
        return ("message" in response
                and response["message"] == "Record deleted successfully")

    def revisions(self):
        """Generator providing all the revisions in the project"""
        revisions = self._api.revisions_read(self.project_id, self.table_id)
        for revision in revisions:
            yield Revision(self._api, self.project_id, self.table_id,
                           revision_details=revision)

    def all_revisions(self) -> Revision:
        """Fetches all revisions of the table

        :return: List of revisions
        :rtype: [Revision]
        """
        return [revision for revision in self.revisions()]

    def revision(self, name: str) -> Revision:
        """Looks up a revision by *name*

        Note: when there are multiple tables with the same *name* the first
        match will be returned.

        :param name: name of the requested revision
        :type name: str
        :raises LookupError: Revision *name* not found
        :return: object of the requested revision
        :rtype: Revision
        """
        for revision in self.revisions():
            if revision.name == name:
                return revision

        raise LookupError("Revision '{}' not found".format(name))

    def revision_by_uuid(self, revision_id: str) -> Revision:
        """Fetches a Revision by its UUID

        :param revision_id: UUID of the revision
        :type revision_id: str
        :return: object of the requested revision
        :rtype: Revision
        """
        return Revision.from_uuids(
            self._api, self.project_id, self.table_id, revision_id)

    def add_revision(self, name: str) -> bool:
        """Add a revision of the table

        :param name: name of the revision
        :type name: str
        :return: ``True`` when the revision was added succesfully
        :rtype: bool
        """
        response = self._api.revision_create(
            self.project_id, self.table_id, name)
        return 'id' in response

    def remove_revision(self, revision: Revision) -> bool:
        """Removes a revision from the project

        :param revision: revision object of the revision that is to be removed
        :type revision: Revision
        :return: ``True`` when the revision was succesfully removed
        :rtype: bool
        """
        response = self._api.revision_delete(
            self.project_id, self.table_id, revision.revision_id)
        return ("message" in response
                and response["message"] == "Resource deleted successfully")

    def search(self, search_phrase: str, search_fields: [str]) -> dict:
        """Searches the table for a phrase in specidic fields of the table

        :param search_phrase: phrase that is to be searched for
        :type search_phrase: str
        :param search_fields: a list with al the names of the fields that needs
            to be looked in. The names are equal to the column names of the
            table
        :type search_fields: [str]
        :return: T.B.D.
        :rtype: dict
        """
        return self._api.search(
            self.project_id, self.table_id, search_phrase, search_fields)
