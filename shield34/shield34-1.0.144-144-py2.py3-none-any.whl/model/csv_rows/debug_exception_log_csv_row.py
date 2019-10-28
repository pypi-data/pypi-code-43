from shield34_reporter.model.csv_rows.log_base_csv_row import LogBaseCsvRow
from shield34_reporter.model.enums.row_sub_type import RowSubType


class DebugExceptionLogCsvRow(LogBaseCsvRow):

    log = ""
    expDesc = None
    exception = None

    def __init__(self, log, exception):
        self.log = log
        self.exception = exception
        if hasattr(exception, 'msg'):
            self.expDesc = exception.msg
        else:
            self.expDesc = ''

        super(DebugExceptionLogCsvRow, self).__init__(RowSubType.DEBUG_EXCEPTION)

    def gen_row_value(self, lst=['log', 'expDesc']):
        row_value = {}
        for a in lst:
            row_value[a] = getattr(self, a)
        return row_value

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value), self.gen_row_value()]