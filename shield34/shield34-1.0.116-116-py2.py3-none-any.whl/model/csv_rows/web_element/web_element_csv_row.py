from shield34_reporter.model.csv_rows.helpers.web_driver_descriptor import WebDriverDescriptor
from shield34_reporter.model.csv_rows.helpers.web_element_descriptor import WebElementDescriptor
from shield34_reporter.model.csv_rows.report_csv_row import ReportCsvRow
from shield34_reporter.model.enums.row_type import RowType


class WebElementCsvRow(ReportCsvRow):
    webElement = None
    driver = None

    def __init__(self, web_element, driver, row_sub_type):
        if web_element is not None:
            self.webElement = WebElementDescriptor(web_element)
        if driver is not None:
            self.driver = WebDriverDescriptor(driver)

        self.rowType = RowType.ACTION
        super(WebElementCsvRow, self).__init__(row_sub_type)

    def gen_row_value(self, lst=['webElement', 'driver']):
        row_value = {}
        for a in lst:
            lst_attr = getattr(self, a)
            if hasattr(lst_attr, 'gen_row_value'):
                row_value[a] = lst_attr.gen_row_value()
            else:
                row_value[a] = lst_attr
        return row_value
