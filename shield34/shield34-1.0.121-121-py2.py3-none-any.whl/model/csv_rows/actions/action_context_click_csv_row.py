import json

from shield34_reporter.model.csv_rows.actions.action_csv_row import ActionCsvRow
from shield34_reporter.model.csv_rows.actions.action_with_element_csv_row import ActionWithWebElementCsvRow
from shield34_reporter.model.enums.row_sub_type import RowSubType


class ActionContextClickCsvRow(ActionCsvRow):

    def __init__(self, driver):
        super(ActionContextClickCsvRow, self).__init__(driver, RowSubType.ACTION_CONTEXT_CLICK)

    def gen_row_value(self, lst=[]):
        row_value = super(ActionContextClickCsvRow, self).gen_row_value()
        for a in lst:
            row_value[a] = getattr(self, a)
        return row_value

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value), json.dumps(self.gen_row_value())]


class ActionContextClickElementCsvRow(ActionWithWebElementCsvRow):
    def __init__(self, driver, web_element):
        super(ActionContextClickElementCsvRow, self).__init__(driver, web_element, RowSubType.ACTION_CONTEXT_CLICK_ELEMENT)

    def gen_row_value(self, lst=[]):
        row_value = super(ActionContextClickElementCsvRow, self).gen_row_value()
        for a in lst:
            row_value[a] = getattr(self, a)
        return row_value

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value), json.dumps(self.gen_row_value())]
