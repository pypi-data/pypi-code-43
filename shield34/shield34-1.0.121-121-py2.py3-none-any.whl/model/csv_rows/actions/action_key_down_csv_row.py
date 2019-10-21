import json

from shield34_reporter.model.csv_rows.actions.action_csv_row import ActionCsvRow
from shield34_reporter.model.csv_rows.actions.action_with_element_csv_row import ActionWithWebElementCsvRow
from shield34_reporter.model.enums.row_sub_type import RowSubType


class ActionKeyDownCsvRow(ActionCsvRow):
    key = ''

    def __init__(self, driver, key):
        self.key = key
        super(ActionKeyDownCsvRow, self).__init__(driver, RowSubType.ACTION_KEY_DOWN)

    def gen_row_value(self, lst=['key']):
        row_value = super(ActionKeyDownCsvRow, self).gen_row_value()
        for a in lst:
            row_value[a] = getattr(self, a)
        return row_value

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value), json.dumps(self.gen_row_value())]


class ActionKeyDownElementCsvRow(ActionWithWebElementCsvRow):
    key = ''

    def __init__(self, driver, web_element, key):
        self.key = key
        super(ActionKeyDownElementCsvRow, self).__init__(driver, web_element, RowSubType.ACTION_KEY_DOWN_ELEMENT)

    def gen_row_value(self, lst=['key']):
        row_value = super(ActionKeyDownElementCsvRow, self).gen_row_value()
        for a in lst:
            row_value[a] = getattr(self, a)
        return row_value

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value), json.dumps(self.gen_row_value())]