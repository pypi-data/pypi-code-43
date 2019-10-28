import re
import time
from datetime import datetime

from shield34_reporter.model.csv_rows.debug_exception_log_csv_row import DebugExceptionLogCsvRow


class TimeUtils():

    @staticmethod
    def get_current_timestamp():
        return int(round(time.time() * 1000.))

    @staticmethod
    def get_timestamp_from_datetime_str(date_str):
        from shield34_reporter.container.run_report_container import RunReportContainer
        try:
            utc_time = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f%z")
        except Exception as e:
            RunReportContainer.add_report_csv_row(
                DebugExceptionLogCsvRow("Couldn't convert datetime str to datetime object. datetime str:" + date_str, e))
            try:
                utc_time = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            except Exception as e:
                RunReportContainer.add_report_csv_row(
                    DebugExceptionLogCsvRow("Couldn't convert datetime str to datetime object. datetime str:" + date_str,
                                            e))
                try:
                    utc_time = TimeUtils.get_datetime_from_iso_datetime_str(date_str)
                except Exception as e:
                    RunReportContainer.add_report_csv_row(
                        DebugExceptionLogCsvRow("Couldn't convert datetime str to datetime object. datetime str:" + date_str, e))


        try:
            epoch_time = int(time.mktime(utc_time.timetuple()) * 1000)
        except:
            epoch_time = int(utc_time.timestamp() * 1000)

        return epoch_time


    @staticmethod
    def get_datetime_from_iso_datetime_str(date_str):
        try:
            conformed_timestamp = re.sub(r"[:]|([-](?!((\d{2}[:]\d{2})|(\d{4}))$))", '', date_str)

            # Split on the offset to remove it. Use a capture group to keep the delimiter
            split_timestamp = re.split(r"[+|-]", conformed_timestamp)
            main_timestamp = split_timestamp[0]
            if len(split_timestamp) == 3:
                sign = split_timestamp[1]
                offset = split_timestamp[2]
            else:
                sign = None
                offset = None

            # Generate the datetime object without the offset at UTC time
            utc_time = datetime.strptime(main_timestamp + "Z", "%Y%m%dT%H%M%S.%fZ")
            if offset:
                # Create timedelta based on offset
                offset_delta = datetime.timedelta(hours=int(sign + offset[:-2]), minutes=int(sign + offset[-2:]))

                # Offset datetime with timedelta
                utc_time = utc_time + offset_delta

            return utc_time
        except Exception as e:
            raise e