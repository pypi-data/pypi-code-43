import json

from shield34_reporter.model.csv_rows.web_element.web_element_csv_row import WebElementCsvRow
from shield34_reporter.model.enums.row_sub_type import RowSubType
from shield34_reporter.model.enums.row_type import RowType


class WebElementClickCsvRow(WebElementCsvRow):

    def __init__(self, web_element, driver):
        self.rowType = RowType.ACTION
        super(WebElementClickCsvRow, self).__init__(web_element, driver, RowSubType.WEB_ELEMENT_CLICK)

    def gen_row_value(self, lst=[]):

        row_value = super(WebElementClickCsvRow, self).gen_row_value()
        for a in lst:
            row_value[a] = getattr(self, a)
        return row_value

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value),
                json.dumps(self.gen_row_value())]