import cx_Oracle
import uuid
from config import ORACLE_SERVER
from utils.code import b64encode
from classcard_dataclient.models.course import CourseTableManager, Course
from classcard_dataclient.models.classroom import Classroom
from classcard_dataclient.client.action import DataClient


class CourseTableSync(object):
    def __init__(self):
        db = cx_Oracle.connect(ORACLE_SERVER, encoding="UTF-8", nencoding="UTF-8")  # 连接数据库
        print(db.version)
        self.cur = db.cursor()
        self.xn = '2019-2020'
        self.xq = '1'
        manager_name = "{}-{}".format(self.xn, self.xq)
        manager_number = b64encode(manager_name)
        self.manager = CourseTableManager(name=manager_name, number=manager_number)
        self.course_map = {}
        self.classroom_map = {}
        self.client = DataClient()

    def analyse_position(self, jc, week):
        course_week = int(week)
        position = []
        jc_items = jc.split('-')
        if len(jc_items) == 1:
            position.append((int(jc_items[0]), course_week))
        elif len(jc_items) == 2:
            for item in range(int(jc_items[0]), int(jc_items[1]) + 1):
                position.append((item, course_week))
        return position

    def get_course(self):
        single_map = {"单": 1, "双": 2}
        sql = "select j.KCDM, j.SKBJH, j.RKJSGH, j.ZC, j.XQJ, j.DSZ, j.JC, j.SKDD, x.XH, x.KCMC " \
              "from V_BZKS_JSKB j join V_BZKS_XSKB x on j.KCDM=x.KCDM " \
              "where j.XN='{}' and j.XQ='{}' and x.XN='{}' and x.XQ='{}' ".format(self.xn, self.xq, self.xn, self.xq)
        self.cur.execute(sql)
        rows = self.cur.fetchall()
        for row in rows:
            number, name = row[0], row[9]
            classroom_name = row[7]
            teacher_number = row[2]
            week_range = row[3]
            num, week = row[4], row[6]
            single = single_map[row[5]]
            begin_week, end_week = week_range.split("-")[0], week_range.split("-")[-1]
            student_number = row[8]
            course_name = name + classroom_name + teacher_number + week_range + num + week
            course_b64 = b64encode(course_name)
            if course_b64 in self.course_map:
                course = self.course_map[course_b64]
            else:
                course_number = str(uuid.uuid4())[:8]
                classroom_num = b64encode(classroom_name)
                if classroom_num not in self.classroom_map:
                    self.classroom_map[classroom_num] = Classroom(number=classroom_num, name=classroom_name)
                subject_number = b64encode(name)
                course = Course(number=course_number, name=name, teacher_number=teacher_number,
                                classroom_number=classroom_num, subject_number=subject_number,
                                begin_week=begin_week, end_week=end_week)
                self.course_map[number] = course
            positions = self.analyse_position(num, week)
            for position in positions:
                course.add_position(position[0], position[1], single)
            course.add_student(student_number)

    def sync(self):
        self.get_course()
        for number, course in self.course_map.items():
            self.manager.add_course(course)
        classrooms = list(self.classroom_map.values())
        self.client.create_classrooms(classrooms)
        self.client.create_course_table(self.manager)
