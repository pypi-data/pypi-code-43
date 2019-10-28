import json

from shield34_reporter.model.csv_rows.report_csv_row import ReportCsvRow
from shield34_reporter.model.enums.row_type import RowType


class InternalActionCsvRow(ReportCsvRow):

    def __init__(self, row_sub_type):
        self.rowType = RowType.INTERNAL_ACTION
        super(InternalActionCsvRow, self).__init__(row_sub_type)

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value), json.dumps("")]