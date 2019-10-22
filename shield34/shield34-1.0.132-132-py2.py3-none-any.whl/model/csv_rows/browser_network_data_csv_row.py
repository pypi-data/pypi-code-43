import json

from shield34_reporter.model.csv_rows.report_csv_row import ReportCsvRow
from shield34_reporter.model.enums.row_sub_type import RowSubType
from shield34_reporter.model.enums.row_type import RowType


class BrowserNetworkDataCsvRow(ReportCsvRow):
    fileName = ''
    fileNameAsPath = ''

    def __init__(self, file_name_as_path, file_name):
        self.fileName = file_name
        self.fileNameAsPath = file_name_as_path
        self.rowType = RowType.BROWSER_NETWORK
        super(BrowserNetworkDataCsvRow, self).__init__(RowSubType.BROWSER_NETWORK)

    def gen_row_value(self, lst=['fileName', 'fileNameAsPath']):

        row_value = {}
        for a in lst:
            row_value[a] = getattr(self, a)
        return row_value

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value),
                json.dumps(self.gen_row_value())]