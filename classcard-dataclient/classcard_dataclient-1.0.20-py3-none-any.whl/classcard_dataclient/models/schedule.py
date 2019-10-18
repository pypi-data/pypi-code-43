import datetime
from ..models.base import BaseModel
from ..utils.dateutils import str2_time, datetime2str, str2datetime


class PeriodSet(object):
    MORNING = "morning"
    NOON = "noon"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"

    MESSAGE = {
        MORNING: "上午",
        NOON: "中午",
        AFTERNOON: "下午",
        EVENING: "傍晚",
        NIGHT: "午夜",
    }


class RestTable(BaseModel):
    def __init__(self, *args, **kwargs):
        self.uid = None
        self.name = None  # 必填*,作息表名称
        self.number = None  # 必填*,作息表编号
        self.category = 0  # 0 单周 1 双周
        self.description = None
        self.schedule_list = []
        super(RestTable, self).__init__(*args, **kwargs)
        self.required_filed = ["name", "number"]

    def spe_validate(self):
        for schedule in self.schedule_list:
            if not isinstance(schedule, RestSchedule):
                raise TypeError("course type must be a models.Course instance")
            schedule.validate()

    def add_schedule(self, rest_schedule):
        """
        增加作息子元素
        :param rest_schedule:作息子元素，Type -> RestSchedule
        :return:
        """
        if not isinstance(rest_schedule, RestSchedule):
            raise TypeError("course type must be a Course")
        self.schedule_list.append(rest_schedule)

    @property
    def schedule(self):
        data = list(map(lambda s: s.nirvana_data, self.schedule_list))
        return data

    @property
    def nirvana_data(self):
        data = {"name": self.name,
                "number": self.number,
                "category": self.category,
                "description": self.description,
                "schedule": self.schedule}
        return data


class RestSchedule(BaseModel):
    def __init__(self, *args, **kwargs):
        self.uid = None
        self.category = 0
        self.name = None
        self.num = None  # 必填*,课程序号
        self.order = None  # 必填*,作息序号
        self.week = None  # 必填*,星期
        self.pre_time = None  # 签到开始时间基线
        self.start_time = None  # 必填*,开始时间
        self.stop_time = None  # 必填*,结束时间
        self.time_period = None  # 时间标签
        super(RestSchedule, self).__init__(*args, **kwargs)
        self.required_filed = ["num", "order", "week", "start_time", "stop_time"]

    def spe_validate(self):
        str2_time(self.start_time)
        str2_time(self.stop_time)

    @property
    def default_pre_time(self):
        """
        预打卡时间缺省值，为开始时间的10分钟之前
        :return:
        """
        fake_start_time = "1970-12-11 {}".format(self.start_time)
        start_time = str2datetime(fake_start_time)
        start_time -= datetime.timedelta(minutes=10)
        datetime_str = datetime2str(start_time)
        default_pre_time = datetime_str.split(" ")[1]
        return default_pre_time

    @property
    def default_name(self):
        """
        节次名称的缺省值
        :return:
        """
        return "第{}课时".format(self.num)

    @property
    def default_time_period(self):
        """
        时间段名称
        morning| 00:00:00 - 12:00:00
        afternoon| 12:00:00  - 18:00:00
        night| 18:00:00  - 23:59:59
        :return:
        """
        morning = str2_time("12:00:00")
        afternoon = str2_time("18:00:00")
        start_time = str2_time(self.start_time)
        if start_time <= morning:
            time_period = PeriodSet.MORNING
        elif morning <= start_time <= afternoon:
            time_period = PeriodSet.AFTERNOON
        else:
            time_period = PeriodSet.NIGHT
        return time_period

    @property
    def nirvana_data(self):
        data = {"name": self.name or self.default_name,
                "num": self.num,
                "order": self.order,
                "week": self.week,
                "pre_time": self.pre_time or self.default_pre_time,
                "start_time": self.start_time,
                "stop_time": self.stop_time,
                "time_period": self.time_period or self.default_time_period,
                "category": self.category}
        return data
