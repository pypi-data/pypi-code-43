from robot.libraries.BuiltIn import BuiltIn
from shield34_reporter.model.csv_rows.debug_exception_log_csv_row import DebugExceptionLogCsvRow


class DriverUtils:

    @staticmethod
    def get_current_driver():
        from shield34_reporter.container.run_report_container import RunReportContainer
        current_driver = None
        try:
            selenium_lib = BuiltIn().get_library_instance('SeleniumLibrary')
        except Exception as e:
            RunReportContainer.add_report_csv_row(
                DebugExceptionLogCsvRow("Couldn't get SeleniumLibrary library.", e))
            try:
                selenium_lib = BuiltIn().get_library_instance('Selenium2Library')
            except Exception as e:
                RunReportContainer.add_report_csv_row(
                    DebugExceptionLogCsvRow("Couldn't get Selenium2Library library.", e))
        try:
            current_driver = selenium_lib._current_browser()
        except Exception as e:
            RunReportContainer.add_report_csv_row(
                DebugExceptionLogCsvRow("Couldn't get current driver with the method _current_browser.", e))
            try:
                current_driver = selenium_lib.driver
            except Exception as e:
                RunReportContainer.add_report_csv_row(
                    DebugExceptionLogCsvRow("Couldn't get current driver with via the driver property", e))
                current_driver = None

        return current_driver


    @staticmethod
    def get_page_html():
        driver = DriverUtils.get_current_driver()
        page_source = ''
        try:
            page_source = driver.page_source
        except Exception as e:
            page_source = ''
        return page_source