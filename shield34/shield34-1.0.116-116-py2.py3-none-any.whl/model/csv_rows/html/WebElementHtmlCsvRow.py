import json

from shield34_reporter.model.csv_rows.report_csv_row import ReportCsvRow
from shield34_reporter.model.enums.row_sub_type import RowSubType
from shield34_reporter.model.enums.row_type import RowType


class WebElementHtml(ReportCsvRow):
    elementHtml = ''
    elementWrappingHtml = ''
    elementComputedCss = ''

    def __init__(self, element_html, element_computed_css, element_wrapping_html):
        self.elementHtml = element_html
        self.elementWrappingHtml = element_wrapping_html
        self.elementComputedCss = element_computed_css
        self.rowType = RowType.HTML
        super(WebElementHtml, self).__init__(RowSubType.WEB_ELEMENT_HTML)

    def gen_row_value(self, lst=['elementHtml', 'elementWrappingHtml', 'elementComputedCss']):

        row_value = {}
        for a in lst:
            row_value[a] = getattr(self, a)
        return row_value

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value), json.dumps(self.gen_row_value())]