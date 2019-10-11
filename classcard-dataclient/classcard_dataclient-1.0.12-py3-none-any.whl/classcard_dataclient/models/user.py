from ..models.base import BaseModel
from ..utils.code import b64encode


class GenderSet(object):
    MALE = 'M'
    FEMALE = "F"

    MESSAGE = {
        MALE: "男",
        FEMALE: "女"
    }


class Teacher(BaseModel):
    uid = None
    number = None
    password = None
    name = None
    description = None
    birthday = None
    ecard = None
    email = None
    gender = GenderSet.MALE
    phone = None
    school = None

    def __init__(self, *args, **kwargs):
        super(Teacher, self).__init__(*args, **kwargs)

    @property
    def sso_data(self):
        data = {"birthday": self.birthday,
                "description": self.description,
                "ecard": self.ecard,
                "email": self.email,
                "gender": self.gender,
                "name": self.name,
                "number": self.number,
                "phone": self.phone,
                "password": b64encode(self.password),
                "school": self.school
                }
        return data


class Student(BaseModel):
    uid = None
    number = None
    password = None
    name = None
    description = None
    birthday = None
    ecard = None
    email = None
    gender = GenderSet.MALE
    phone = None
    classof = None
    graduateat = None
    class_name = None
    section = None
    school = None

    def __init__(self, *args, **kwargs):
        super(Student, self).__init__(*args, **kwargs)
        self.class_id = None

    @property
    def sso_data(self):
        data = {"birthday": self.birthday,
                "description": self.description,
                "ecard": self.ecard,
                "email": self.email,
                "gender": self.gender,
                "name": self.name,
                "number": self.number,
                "phone": self.phone,
                "password": b64encode(self.password),
                "classof": self.classof,
                "graduateat": self.graduateat,
                "section": self.class_id or self.section}
        return data
