import json

from shield34_reporter.model.csv_rows.helpers.time_utils import TimeUtils
from shield34_reporter.model.csv_rows.report_csv_row import ReportCsvRow
from shield34_reporter.model.enums.row_sub_type import RowSubType
from shield34_reporter.model.enums.row_type import RowType


class EndTimeCsvRow(ReportCsvRow):
    endTime = ""

    def __init__(self, end_time):
        self.rowType = RowType.TEST_END_TIME
        self.endTime = str(TimeUtils.convert_timestamp_to_millis(end_time))
        super(EndTimeCsvRow, self).__init__(RowSubType.TEST_END_TIME)

    def gen_row_value(self, lst=['endTime']):

        row_value = {}
        for a in lst:
            row_value[a] = getattr(self, a)
        return row_value

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value),
                json.dumps(self.gen_row_value())]