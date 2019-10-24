from shield34_reporter.model.csv_rows.browser.browser_console_csv_row import BrowserConsoleLogCsvRow
from shield34_reporter.model.enums.row_sub_type import RowSubType


class BrowserConsoleLogsHelper():

    @staticmethod
    def add_browser_logs_to_report(logEntry):
        from shield34_reporter.container.run_report_container import RunReportContainer
        if logEntry['level'] == 'SEVERE' :
            RunReportContainer.add_report_csv_row(BrowserConsoleLogCsvRow(RowSubType.BROWSER_CONSOLE_ERROR, logEntry['timestamp'], logEntry['message']))
        elif logEntry['level'] == 'INFO' :
            RunReportContainer.add_report_csv_row(BrowserConsoleLogCsvRow(RowSubType.BROWSER_CONSOLE_INFO, logEntry['timestamp'], logEntry['message']))
        elif logEntry['level'] == 'WARNING' :
            RunReportContainer.add_report_csv_row(BrowserConsoleLogCsvRow(RowSubType.BROWSER_CONSOLE_WARN, logEntry['timestamp'], logEntry['message']))
        elif logEntry['level'] == 'FINE' :
            RunReportContainer.add_report_csv_row(BrowserConsoleLogCsvRow(RowSubType.BROWSER_CONSOLE_DEBUG, logEntry['timestamp'], logEntry['message']))