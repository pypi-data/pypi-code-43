import json

from shield34_reporter.model.csv_rows.helpers.web_driver_descriptor import WebDriverDescriptor
from shield34_reporter.model.csv_rows.report_csv_row import ReportCsvRow
from shield34_reporter.model.enums.row_sub_type import RowSubType
from shield34_reporter.model.enums.row_type import RowType


class WebDriverQuitCsvRow(ReportCsvRow):
    driver = None

    def __init__(self, driver):
        self.driver = WebDriverDescriptor(driver)
        self.rowType = RowType.ACTION
        super(WebDriverQuitCsvRow, self).__init__(RowSubType.WEB_DRIVER_QUIT)

    def gen_row_value(self, lst=['driver']):

        row_value = {}
        for a in lst:
            lst_attr = getattr(self, a)
            if hasattr(lst_attr, 'gen_row_value'):
                row_value[a] = lst_attr.gen_row_value()
            else:
                row_value[a] = lst_attr
        return row_value

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value),
                json.dumps(self.gen_row_value())]