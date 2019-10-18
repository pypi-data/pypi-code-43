from ..models.base import BaseModel


class ModeType(object):
    MODE_COMMON = 1
    MODE_EMERGENCY = 2
    MODE_EXAM = 3
    MODE_MEETING = 4
    MODE_VIDEO = 5

    MESSAGE = {
        MODE_COMMON: "普通模式",
        MODE_EMERGENCY: "通知模式",
        MODE_EXAM: "考试模式",
        MODE_MEETING: '会议模式',
        MODE_VIDEO: '视频模式',
    }


class RoomType(object):
    TYPE_CLASS = 1
    TYPE_PUBLIC = 2

    MESSAGE = {
        TYPE_CLASS: "班级教室",
        TYPE_PUBLIC: "公共教室",
    }


class Classroom(BaseModel):
    def __init__(self, *args, **kwargs):
        self.name = None
        self.category = RoomType.TYPE_CLASS
        self.seats = 1
        self.number = None
        self.building = None
        self.floor = None
        self.section_name = None
        self.mode = ModeType.MODE_COMMON
        self.extra_info = None
        self.school = None
        super(Classroom, self).__init__(*args, **kwargs)
        self.section_id = None
        self.required_filed = ["name", "number", "seats", "category"]

    @property
    def nirvana_data(self):
        data = {"name": self.name,
                "category": self.category,
                "seats": int(self.seats),
                "num": self.number,
                "building": self.building,
                "floor": self.floor,
                "mode": self.mode}
        if self.section_id:
            data["section"] = {"uid": self.section_id}
        return data
