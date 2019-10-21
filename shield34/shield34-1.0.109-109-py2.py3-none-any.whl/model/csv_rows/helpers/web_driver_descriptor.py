class WebDriverDescriptor():
    browser = ''

    def __init__(self, driver):
        if driver is not None:
            self.browser = driver.name

    def gen_row_value(self, lst=['browser']):
        row_value = {}

        for a in lst:
            row_value[a] = getattr(self, a)
        return row_value
