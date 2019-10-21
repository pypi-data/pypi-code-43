import json

from shield34_reporter.model.csv_rows.report_csv_row import ReportCsvRow
from shield34_reporter.model.enums.row_type import RowType


class BrowserConsoleLogCsvRow(ReportCsvRow):
    content = ''

    def __init__(self, row_sub_type, timestamp, content):
        self.rowType = RowType.BROWSER_CONSOLE
        self.timestamp = timestamp
        self.content = content
        super(BrowserConsoleLogCsvRow, self).__init__(row_sub_type)

    def gen_row_value(self, lst=['content']):

        row_value = {}
        for a in lst:
            row_value[a] = getattr(self, a)
        return row_value

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value), json.dumps(self.gen_row_value())]