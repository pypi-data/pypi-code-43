from shield34_reporter.container.run_report_container import RunReportContainer


class WebElementDescriptor():
    locator = ''

    def __init__(self, web_element):
        web_element_locator = RunReportContainer.get_current_block_run_holder().get_web_element(web_element.id)
        self.locator = web_element_locator

    def gen_row_value(self, lst=['locator']):
        row_value = {}

        for a in lst:
            row_value[a] = getattr(self, a)
        return row_value




