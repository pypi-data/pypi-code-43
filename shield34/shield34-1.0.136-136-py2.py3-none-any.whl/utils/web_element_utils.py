from selenium.webdriver.common.by import By

from shield34_reporter.model.csv_rows.debug_exception_log_csv_row import DebugExceptionLogCsvRow


class WebElementUtils():

    @staticmethod
    def get_element_html(web_element):
        return web_element.get_attribute("outerHTML")

    @staticmethod
    def get_element_computed_css(web_element, driver):
        from shield34_reporter.container.run_report_container import RunReportContainer
        element_css = ''
        try:
            element_css = driver.execute_script("var cssObj = window.getComputedStyle(arguments[0], null);" +
                                        "var result = {};" +
                                        "for (var i=0; i<cssObj.length; i++) {" +
                                        "cssObjProp = cssObj.item(i);" +
                                        "result[cssObjProp] = cssObj.getPropertyValue(cssObjProp);" +
                                    "}" +
                                    "return JSON.stringify(result);", web_element)
        except Exception as e:
            RunReportContainer.add_report_csv_row(DebugExceptionLogCsvRow("Couldn't calculate element computed css", e))

        return str(element_css)

    @staticmethod
    def get_element_wrapping_html(web_element, wrapping_levels):
        i = 0
        while i < wrapping_levels and web_element.tag_name != 'body':
            web_element = web_element.org_find_element(By.XPATH, '..')
            i += 1
        return web_element.get_attribute("outerHTML")