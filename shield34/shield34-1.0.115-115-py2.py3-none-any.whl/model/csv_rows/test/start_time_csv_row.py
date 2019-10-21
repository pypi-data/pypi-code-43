import json

from shield34_reporter.model.csv_rows.helpers.time_utils import TimeUtils
from shield34_reporter.model.csv_rows.report_csv_row import ReportCsvRow
from shield34_reporter.model.enums.row_sub_type import RowSubType
from shield34_reporter.model.enums.row_type import RowType


class StartTimeCsvRow(ReportCsvRow):
    startTime = ""

    def __init__(self, start_time):
        self.startTime = str(TimeUtils.convert_timestamp_to_millis(start_time))
        self.rowType = RowType.TEST_START_TIME
        super(StartTimeCsvRow, self).__init__(RowSubType.TEST_START_TIME)

    def gen_row_value(self, lst=['startTime']):

        row_value = {}
        for a in lst:
            row_value[a] = getattr(self, a)
        return row_value

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value),
                json.dumps(self.gen_row_value())]