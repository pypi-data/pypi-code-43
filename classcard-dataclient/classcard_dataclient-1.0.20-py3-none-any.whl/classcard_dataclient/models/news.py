from ..models.base import BaseModel
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


class News(BaseModel):
    def __init__(self, *args, **kwargs):
        self.uid = None
        self.title = None  # 必填*
        self.content = None  # 必填*
        self.description = None
        self.category = TypeSet.SCHOOL_TYPE
        self.school = None
        self.class_name = None
        self.classroom_numbers = []
        super(News, self).__init__(*args, **kwargs)
        self.required_filed = ['title', 'content']
        self.class_id = None
        self.classroom_ids = []

    def add_classroom(self, classroom_number):
        self.classroom_numbers.append(classroom_number)

    def spe_validate(self):
        if self.category == TypeSet.CLASS_TYPE and not self.class_name:
            raise ValidateError("If category is CLASS_TYPE, class_name is required")

    @property
    def nirvana_data(self):
        data = {"title": self.title,
                "content": self.content,
                "description": self.description,
                "category": self.category}
        if self.category == TypeSet.CLASS_TYPE and self.class_id:
            data['owner'] = {"uid": self.class_id}
        return data
