import json

from shield34_reporter.model.csv_rows.report_csv_row import ReportCsvRow
from shield34_reporter.model.enums.row_sub_type import RowSubType
from shield34_reporter.model.enums.row_type import RowType


class PageHtml(ReportCsvRow):
    pageHtml = ''

    def __init__(self, page_html):
        self.pageHtml = page_html
        self.rowType = RowType.HTML
        super(PageHtml, self).__init__(RowSubType.PAGE_HTML)

    def gen_row_value(self, lst=['pageHtml']):

        row_value = {}
        for a in lst:
            row_value[a] = getattr(self, a)
        return row_value

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value), json.dumps(self.gen_row_value())]