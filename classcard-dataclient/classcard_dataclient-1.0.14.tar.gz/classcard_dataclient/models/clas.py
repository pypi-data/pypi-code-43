from ..models.base import BaseModel


class Class(BaseModel):
    uid = None
    name = None
    number = None
    description = None
    principal_number = None  # 班主任工号
    motto = None
    grade = None
    teacher_list = []
    student_list = []
    school = None

    def __init__(self, *args, **kwargs):
        super(Class, self).__init__(*args, **kwargs)
        self.principal_id = None
        self.teacher_ids = []
        self.student_ids = []

    def add_student(self, student_number):
        self.student_list.append(student_number)

    def add_teacher(self, teacher_number):
        self.teacher_list.append(teacher_number)

    @property
    def teachers(self):
        return ",".join(self.teacher_ids)

    @property
    def students(self):
        return ",".join(self.student_ids)

    @property
    def sso_data(self):
        data = {"name": self.name,
                "description": self.description,
                "number": self.number,
                "principal_id": self.principal_id,
                "motto": self.motto,
                "grade": self.grade}
        return data
