import time

from robot.libraries.BuiltIn import BuiltIn

from shield34_reporter.container.run_report_container import RunReportContainer
from shield34_reporter.model.csv_rows.debug_exception_log_csv_row import DebugExceptionLogCsvRow
from shield34_reporter.model.csv_rows.screen_shot_csv_row import ScreenShotCsvRow
from shield34_reporter.model.csv_rows.test.test_failure_screen_shot import TestFailureScreenShot
from shield34_reporter.model.enums.file_type import FileType
from shield34_reporter.utils.driver_utils import DriverUtils
from shield34_reporter.utils.file_handler import upload_file


class ScreenShot():

    @staticmethod
    def capture_screen_shoot(file_name, placement, on_failure = False):
        from shield34_reporter.model.contracts.s3_file_details import S3FileDetails
        from shield34_reporter.utils.aws_utils import AwsUtils
        screen_shot_file = None
        try:
            current_driver = DriverUtils.get_current_driver()
            screen_shot_file = current_driver.get_screenshot_as_png()
        except Exception as e:
            RunReportContainer.add_report_csv_row(DebugExceptionLogCsvRow("Error while taking screenshot", e))

        block_run_contract = RunReportContainer.get_current_block_run_holder().blockRunContract
        timestamp = str(int(round(time.time() * 1000.)))
        file_name_to_save = timestamp + "-" + file_name + "-" + placement + ".png"
        if screen_shot_file is not None:
            screen_shot_details_contract = S3FileDetails(block_run_contract.runContract['id'], block_run_contract.id,
                                                         file_name_to_save, FileType.SCREEN_SHOT.value)
            pre_signed_url_contract = AwsUtils.get_file_upload_to_s3_url(screen_shot_details_contract)
            RunReportContainer.get_current_block_run_holder().pool.submit(upload_file,
                                                                            pre_signed_url_contract.url,
                                                                            screen_shot_file)
            if on_failure:
                RunReportContainer.add_report_csv_row(TestFailureScreenShot(pre_signed_url_contract.fileName, placement))
            else:
                RunReportContainer.add_report_csv_row(ScreenShotCsvRow(pre_signed_url_contract.fileName, placement))



