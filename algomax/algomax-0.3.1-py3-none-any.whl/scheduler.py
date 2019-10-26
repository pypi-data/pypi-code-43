from datetime import datetime
import time

import schedule

from .user_schedule_data import UserScheduleData
from .schedule_type import ScheduleType
from algomax_common.terminal import FontColor
from . import messages


DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
START_TIME_SUFFIX = '00:00:00'
END_TIME_SUFFIX = '23:59:59'


class Scheduler:
    """
    scheduler class
    this class handles schedule functionality for algomax
    """
    count = 1

    def __init__(self, schedule_data: UserScheduleData, func_job, *args):
        self.schedule_data = schedule_data
        self.func_job = func_job
        self.job_args = args
        self.end_time_error_showed = False
        self.off_day_error_showed = False
        self.future_schedule_datetime_showed = False
        self.long_future_schedule_datetime_showed = False
        self.job = None
        self.__initiate()

    def __initiate(self):
        """
        initiate the scheduler
        """
        if self.schedule_data.mode == ScheduleType.INTERVAL:
            start_date_str = '{0} {1}'.format(self.schedule_data.schedule['start_date'], START_TIME_SUFFIX)
            start_time_str = self.schedule_data.schedule['start_time']
            self.start_hour, self.start_minute = map(lambda x: int(x), start_time_str.split(':'))
            self.start_date = datetime.strptime(start_date_str, DATE_FORMAT)
            end_date_str = '{0} {1}'.format(self.schedule_data.schedule['end_date'], END_TIME_SUFFIX)
            end_time_str = self.schedule_data.schedule['end_time']
            self.end_hour, self.end_minute = map(lambda x: int(x), end_time_str.split(':'))
            self.end_date = datetime.strptime(end_date_str, DATE_FORMAT)

            self.minute_interval = self.schedule_data.schedule['minutes_interval']

            self.valid_days_of_week = self.schedule_data.schedule.get('days_of_week', [])

            self.now = datetime.now()

            self.start_date_time = self.now.replace(hour=self.start_hour, minute=self.start_minute, second=0)
            self.end_date_time = self.now.replace(hour=self.end_hour, minute=self.end_minute, second=0)

            self.current_day_of_week = datetime.now().weekday()

    def start(self):
        """
        this method starts the scheduler instance
        """
        if self.schedule_data.mode == ScheduleType.ONCE:
            self.func_job(*self.job_args)
        elif self.schedule_data.mode == ScheduleType.INTERVAL:
            self.job = schedule.every(self.minute_interval).minutes.do(self.func_job, *self.job_args)
            while True:
                if self.start_date > self.now and self.end_date > self.now:
                    days = (self.start_date - self.now).days
                    if not self.future_schedule_datetime_showed and days <= 0:
                        print(FontColor.failed(FontColor.bold(messages.FUTURE_SCHEDULE_DATE)))
                        self.future_schedule_datetime_showed = True
                    if not self.long_future_schedule_datetime_showed and days > 0:
                        print(FontColor.failed(FontColor.bold(messages.LONG_FUTURE_SCHEDULE_DATE.format(days))))
                        self.long_future_schedule_datetime_showed = True
                elif self.start_date <= self.now <= self.end_date:  # state 0 yes
                    self.future_schedule_datetime_showed = False
                    self.long_future_schedule_datetime_showed = False
                    if not len(self.valid_days_of_week) or self.current_day_of_week in self.valid_days_of_week:  # state 1 yes
                        self.off_day_error_showed = False
                        if self.start_date_time <= self.now <= self.end_date_time:  # state 2 yes
                            self.end_time_error_showed = False
                            schedule.run_pending()
                            time.sleep(1)
                        else:  # state 2 no
                            if self.now > self.end_date_time and self.now.date() == self.end_date.date():  # state 3 yes
                                print(FontColor.failed(FontColor.bold(messages.EXPIRE_SCHEDULE_DATE)))
                                self.stop()

                            if not self.end_time_error_showed:
                                self.end_time_error_showed = True
                                print(FontColor.failed(FontColor.bold(messages.END_TIME)))
                    else: # state 1 no
                        if self.now.date() == self.end_date.date(): # state 4 yes
                            print(FontColor.failed(FontColor.bold(messages.EXPIRE_SCHEDULE_DATE)))
                            self.stop()

                        if not self.off_day_error_showed:
                            self.off_day_error_showed = True
                            print(FontColor.failed(FontColor.bold(messages.OFF_DAY)))

                    self.__update_date_and_time()

                else:  # state 0 no
                    print(FontColor.failed(FontColor.bold(messages.EXPIRE_SCHEDULE_DATE)))
                    self.stop()

    def stop(self):
        """
        this method stops the scheduler
        """
        if self.schedule_data.mode == ScheduleType.ONCE:
            exit(0)
        elif self.schedule_data.mode == ScheduleType.INTERVAL:
            if self.job is not None:
                schedule.cancel_job(self.job)
                exit(0)

    def __update_date_and_time(self):
        """
        this method updates - date and time - per second for the scheduler
        """
        self.now = datetime.now()
        self.current_day_of_week = self.now.weekday()
        self.start_date_time = self.now.replace(hour=self.start_hour, minute=self.start_minute, second=0)
        self.end_date_time = self.now.replace(hour=self.end_hour, minute=self.end_minute, second=0)

