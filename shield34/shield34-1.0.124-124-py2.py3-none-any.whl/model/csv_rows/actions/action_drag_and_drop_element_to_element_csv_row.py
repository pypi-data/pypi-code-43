import json

from shield34_reporter.model.csv_rows.actions.action_csv_row import ActionCsvRow
from shield34_reporter.model.csv_rows.helpers.web_element_descriptor import WebElementDescriptor
from shield34_reporter.model.enums.row_sub_type import RowSubType


class ActionDragAndDropElementToElementCsvRow(ActionCsvRow):
    sourceWebElement = None
    targetWebElement = None

    def __init__(self, driver, source_web_element, target_web_element):
        self.sourceWebElement = WebElementDescriptor(source_web_element)
        self.targetWebElement = WebElementDescriptor(target_web_element)
        super(ActionDragAndDropElementToElementCsvRow, self).__init__(driver, RowSubType.ACTION_DRAG_AND_DROP_ELEMENT_TO_ELEMENT)

    def gen_row_value(self, lst=['sourceWebElement', 'targetWebElement']):
        row_value = super(ActionDragAndDropElementToElementCsvRow, self).gen_row_value()
        for a in lst:
            lst_attr = getattr(self, a)
            if hasattr(lst_attr, 'gen_row_value'):
                row_value[a] = lst_attr.gen_row_value()
            else:
                row_value[a] = lst_attr
        return row_value

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value), json.dumps(self.gen_row_value())]