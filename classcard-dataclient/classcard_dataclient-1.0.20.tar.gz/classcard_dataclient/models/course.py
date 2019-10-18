from ..models.base import BaseModel


class CourseCategory(object):
    CLASS = 0
    MIX = 1

    MESSAGE = {
        CLASS: "班级教学班",
        MIX: "混合教学班"
    }


class CourseTableManager(BaseModel):

    def __init__(self, *args, **kwargs):
        self.uid = None
        self.name = None  # 必填*
        self.category = 0  # 0 单周 1 双周
        self.number = None  # 必填*
        self.is_walking = True  # 学校教学模式，是否走班
        self.begin_date = None
        self.end_date = None
        self.courses = []
        super(CourseTableManager, self).__init__(*args, **kwargs)
        self.required_filed = ["name", "number"]

    def spe_validate(self):
        appeared_number = []
        for course in self.courses:
            if not isinstance(course, Course):
                raise TypeError("course type must be a models.Course instance")
            course.validate()
            if course.number in appeared_number:
                raise ValueError("course number should be unique")
            appeared_number.append(course.number)

    def add_course(self, course):
        """
        增加该课程表上的课程
        :param course: 课程，Type -> Course
        :return:
        """
        if not isinstance(course, Course):
            raise TypeError("course type must be a Course")
        self.courses.append(course)

    @property
    def nirvana_data(self):
        data = {"name": self.name,
                "number": self.number,
                "category": self.category,
                "begin_date": self.begin_date,
                "end_date": self.end_date}
        return data


class Course(BaseModel):
    def __init__(self, *args, **kwargs):
        self.uid = None
        self.name = None  # 必填*
        self.number = None  # 必填*，Unique Field*
        self.subject_number = None  # 必填*,科目编号
        self.classroom_number = None  # 教室编号
        self.class_name = None  # 班级名称,非走班必填
        self.teacher_number = None  # 老师工号
        self.manager_number = None  # 课程表编号
        self.is_walking = True  # 是否走班,一般等于课程表属性
        self.is_present = True  # 是否签到
        self.begin_week = None
        self.end_week = None
        self.student_list = []
        self.schedule = []  # (num,week)
        self.required_student = True
        super(Course, self).__init__(*args, **kwargs)
        self.subject_id = None
        self.classroom_id = None
        self.class_id = None
        self.teacher_id = None
        self.manager_id = None
        self.student_ids = []
        self.required_filed = ['name', 'number', 'subject_number']

    def spe_validate(self):
        if not self.is_walking and self.class_name is None:
            raise ValueError("班级名称,非走班必填")

    def add_position(self, num, week, category):
        """
        增加课程表上的课位
        :param num: 节次数
        :param week: 星期数
        :param category: 单双周 0: 全周, 1:单周 2:双州
        :return:
        """
        if (num, week, category) not in self.schedule:
            self.schedule.append((num, week, category))

    def add_student(self, student_number):
        """
        增加课程成员
        :param student_number:学生的学号
        :return:
        """
        if student_number not in self.student_list:
            self.student_list.append(student_number)

    @property
    def nirvana_data(self):
        data = {"classroom": self.classroom_id,
                "is_present": self.is_present,
                "is_walking": self.is_walking,
                "begin_week": self.begin_week,
                "end_week": self.end_week,
                "num": self.number, "name": self.name,
                "student": self.student_ids,
                "subject": self.subject_id,
                "teacher": self.teacher_id}
        if not self.is_walking:
            data["section"] = self.class_id
        return data
