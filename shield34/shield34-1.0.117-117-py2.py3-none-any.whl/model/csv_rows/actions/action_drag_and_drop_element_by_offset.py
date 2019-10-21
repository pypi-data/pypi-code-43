import json

from shield34_reporter.model.csv_rows.actions.action_with_element_csv_row import ActionWithWebElementCsvRow
from shield34_reporter.model.enums.row_sub_type import RowSubType


class ActionDragAndDropElementByOffset(ActionWithWebElementCsvRow):

    xOffset = 0
    yOffset = 0

    def __init__(self, driver, web_element, x_offset, y_offset):
        self.xOffset = x_offset
        self.yOffset = y_offset
        super(ActionDragAndDropElementByOffset, self).__init__(driver, web_element, RowSubType.ACTION_DRAG_AND_DROP_ELEMENT_BY_OFFSET)

    def gen_row_value(self, lst=['xOffset', 'yOffset']):
        row_value = super(ActionDragAndDropElementByOffset, self).gen_row_value()
        for a in lst:
            row_value[a] = getattr(self, a)
        return row_value

    def to_array(self):
        return [str(int(round(self.timestamp * 1000.))), str(self.rowSubType.value), str(self.rowType.value), json.dumps(self.gen_row_value())]
