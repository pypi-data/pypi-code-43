import json

from shield34_reporter.model.csv_rows.report_csv_row import ReportCsvRow
from shield34_reporter.model.enums.row_sub_type import RowSubType
from shield34_reporter.model.enums.row_type import RowType


class ActionStartedCsvRow(ReportCsvRow):
    def __init__(self):
        self.rowType = RowType.TEST_ACTION
        super(ActionStartedCsvRow, self).__init__(RowSubType.ACTION_STARTED)

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value), json.dumps("")]