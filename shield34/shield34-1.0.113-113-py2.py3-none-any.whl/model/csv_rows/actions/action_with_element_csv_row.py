from shield34_reporter.model.csv_rows.actions.action_csv_row import ActionCsvRow
from shield34_reporter.model.csv_rows.helpers.web_element_descriptor import WebElementDescriptor


class ActionWithWebElementCsvRow(ActionCsvRow):

    webElement = None

    def __init__(self, driver, web_element, row_sub_type):
        self.webElement = WebElementDescriptor(web_element)
        super(ActionWithWebElementCsvRow, self).__init__(driver, row_sub_type)

    def gen_row_value(self, lst=['webElement']):
        row_value = {}
        for a in lst:
            lst_attr = getattr(self, a)
            if hasattr(lst_attr, 'gen_row_value'):
                row_value[a] = lst_attr.gen_row_value()
            else:
                row_value[a] = lst_attr
        return row_value
