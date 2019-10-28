import json

from shield34_reporter.model.csv_rows.actions.action_csv_row import ActionCsvRow
from shield34_reporter.model.csv_rows.actions.action_with_element_csv_row import ActionWithWebElementCsvRow
from shield34_reporter.model.enums.row_sub_type import RowSubType


class ActionSendKeysCsvRow(ActionCsvRow):
    key = ''

    def __init__(self, driver, *keys):
        for key in keys:
            self.key += key
        super(ActionSendKeysCsvRow, self).__init__(driver, RowSubType.ACTION_SEND_KEYS)

    def gen_row_value(self, lst=['key']):
        row_value = super(ActionSendKeysCsvRow, self).gen_row_value()
        for a in lst:
            row_value[a] = getattr(self, a)
        return row_value

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value), json.dumps(self.gen_row_value())]


class ActionSendKeysWithElementCsvRow(ActionWithWebElementCsvRow):
    key = ''

    def __init__(self, driver, web_element, *keys):
        for key in keys:
            self.key += key
        super(ActionSendKeysWithElementCsvRow, self).__init__(driver, web_element, RowSubType.ACTION_SEND_KEYS_ELEMENT)

    def gen_row_value(self, lst=['key']):
        row_value = super(ActionSendKeysWithElementCsvRow, self).gen_row_value()
        for a in lst:
            row_value[a] = getattr(self, a)
        return row_value

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value), json.dumps(self.gen_row_value())]
