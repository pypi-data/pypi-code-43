import json

from shield34_reporter.model.csv_rows.report_csv_row import ReportCsvRow
from shield34_reporter.model.enums.row_sub_type import RowSubType
from shield34_reporter.model.enums.row_type import RowType


class ScreenShotCsvRow(ReportCsvRow):
    fileNameAsPath = ''
    placement = ''

    def __init__(self, file_name_as_path, placement):
        self.rowType = RowType.INTERNAL_ACTION
        self.fileNameAsPath = file_name_as_path
        self.placement = placement
        super(ScreenShotCsvRow, self).__init__(RowSubType.SCREEN_SHOT)

    def gen_row_value(self, lst=['fileNameAsPath', 'placement']):
        row_value = {}
        for a in lst:
            row_value[a] = getattr(self, a)
        return row_value

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value),
                json.dumps(self.gen_row_value())]