import json

from shield34_reporter.model.csv_rows.web_element.web_element_csv_row import WebElementCsvRow
from shield34_reporter.model.enums.row_sub_type import RowSubType
from shield34_reporter.model.enums.row_type import RowType


class WebElementFindElementsCsvRow(WebElementCsvRow):
    locator = ''

    def __init__(self, web_element, driver, locator):
        self.locator = locator
        self.rowType = RowType.ACTION
        super(WebElementFindElementsCsvRow, self).__init__(web_element, driver, RowSubType.WEB_ELEMENT_FIND_ELEMENTS)

    def gen_row_value(self, lst=['locator']):

        row_value = super(WebElementFindElementsCsvRow, self).gen_row_value()
        for a in lst:
            row_value[a] = getattr(self, a)
        return row_value

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value),
                json.dumps(self.gen_row_value())]
