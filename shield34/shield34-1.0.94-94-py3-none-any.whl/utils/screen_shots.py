import time

from robot.libraries.BuiltIn import BuiltIn

from shield34_reporter.container.run_report_container import RunReportContainer
from shield34_reporter.model.csv_rows.screen_shot_csv_row import ScreenShotCsvRow
from shield34_reporter.model.csv_rows.test.test_failure_screen_shot import TestFailureScreenShot
from shield34_reporter.utils.file_handler import upload_file


class ScreenShot():

    @staticmethod
    def capture_screen_shoot(file_name, placement, on_failure = False):
        screen_shot_file = None
        try:
            seleniumlib = BuiltIn().get_library_instance('SeleniumLibrary')
            screen_shot_file = seleniumlib._current_browser().get_screenshot_as_png()
        except:
            pass
                ## TODO RunReportContainer.addReportCsvRow(new
            # DebugExceptionLogCsvRow("An exception was thrown at takeScreenShot.", e));
        block_run_contract = RunReportContainer.get_current_block_run_holder().blockRunContract
        timestamp = str(int(round(time.time() * 1000.)))
        file_name_to_save = timestamp + "-" + file_name + "-" + placement + ".png"
        if screen_shot_file is not None:
            if on_failure:
                RunReportContainer.add_report_csv_row(TestFailureScreenShot(file_name_to_save, placement))
            else:
                RunReportContainer.add_report_csv_row(ScreenShotCsvRow(file_name_to_save, placement))
            RunReportContainer.get_current_block_run_holder().pool.submit(upload_file,
                                                                          block_run_contract.runContract['id'],
                                                                          block_run_contract.id, file_name_to_save,
                                                                          screen_shot_file)



