from ..models.base import BaseModel
from ..utils.dateutils import str2datetime
from ..utils.exceptions import ValidateError


class TypeSet(object):
    CLASS_TYPE = 1
    SCHOOL_TYPE = 2
    CLASSROOM_TYPE = 3

    MESSAGE = {
        CLASS_TYPE: "班级",
        SCHOOL_TYPE: "学校",
        CLASSROOM_TYPE: "教室"
    }


class Video(BaseModel):

    def __init__(self, *args, **kwargs):
        self.uid = None
        self.name = None  # 必填*
        self.path = None  # 必填*
        self.active_start = None
        self.active_end = None
        self.description = None
        self.cover = None
        self.category = TypeSet.SCHOOL_TYPE
        self.school = None
        self.class_name = None
        self.classroom_numbers = []
        super(Video, self).__init__(*args, **kwargs)
        self.required_filed = ['name', 'path']
        self.class_id = None
        self.classroom_ids = []

    def add_classroom(self, classroom_number):
        self.classroom_numbers.append(classroom_number)

    def spe_validate(self):
        str2datetime(self.active_start)
        str2datetime(self.active_end)
        if self.category == TypeSet.CLASS_TYPE and not self.class_name:
            raise ValidateError("If category is CLASS_TYPE, class_name is required")

    @property
    def nirvana_data(self):
        data = {"title": self.name,
                "description": self.description,
                "path": self.path,
                "cover": self.cover,
                "category": self.category,
                "active_start": self.active_start,
                "active_end": self.active_end}
        if self.category == TypeSet.CLASS_TYPE and self.class_id:
            data['owner'] = {"uid": self.class_id}
        return data
