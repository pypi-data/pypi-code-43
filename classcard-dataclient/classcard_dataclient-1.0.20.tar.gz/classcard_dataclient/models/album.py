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


class Album(BaseModel):
    def __init__(self, *args, **kwargs):
        self.uid = None
        self.name = None  # 必填*
        self.category = TypeSet.SCHOOL_TYPE
        self.school = None
        self.class_name = None
        self.classroom_numbers = []
        self.images = []
        super(Album, self).__init__(*args, **kwargs)
        self.required_filed = ['name']
        self.class_id = None
        self.classroom_ids = []

    def add_image(self, image):
        if not isinstance(image, Image):
            raise TypeError("image must be a Image instance")
        self.images.append(image)

    def add_classroom(self, classroom_number):
        self.classroom_numbers.append(classroom_number)

    def spe_validate(self):
        if self.category == TypeSet.CLASS_TYPE and not self.class_name:
            raise ValidateError("If category is CLASS_TYPE, class_name is required")
        for img in self.images:
            if not isinstance(img, Image):
                raise TypeError("image must be a Image instance")
            img.validate()

    @property
    def nirvana_data(self):
        data = {"name": self.name,
                "category": self.category}
        if self.category == TypeSet.CLASS_TYPE and self.class_id:
            data['owner'] = {"uid": self.class_id}
        return data


class Image(BaseModel):
    def __init__(self, *args, **kwargs):
        self.album_name = None
        self.album_category = None
        self.description = ""
        self.name = None  # 必填*
        self.path = None  # 必填*
        super(Image, self).__init__(*args, **kwargs)
        self.required_filed = ['name', "path"]
        self.album_id = None

    @property
    def nirvana_data(self):
        if not self.album_id:
            raise ValueError("album_id is required")
        data = {"name": self.name,
                "path": self.path,
                "description": self.description,
                "album": self.album_id}
        return data
