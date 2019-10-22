import json

from shield34_reporter.model.csv_rows.log_base_csv_row import LogBaseCsvRow
from shield34_reporter.model.enums.row_sub_type import RowSubType


class StepFailedCsvRow(LogBaseCsvRow):
    failureDetailedMessage = ""

    def __init__(self, failure_detailed_message):
        self.failureDetailedMessage = failure_detailed_message
        super(StepFailedCsvRow, self).__init__(RowSubType.STEP_FAILED)

    def gen_row_value(self, lst=['failureDetailedMessage']):

        row_value = {}
        for a in lst:
            row_value[a] = getattr(self, a)
        return row_value

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value), json.dumps(self.gen_row_value())]