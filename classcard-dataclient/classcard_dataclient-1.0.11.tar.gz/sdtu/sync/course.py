import cx_Oracle
import uuid
from sync.base import BaseSync
from config import ORACLE_SERVER
from utils.code import b64encode
from classcard_dataclient.models.course import CourseTableManager, Course
from classcard_dataclient.models.classroom import Classroom
from classcard_dataclient.models.subject import Subject


class CourseTableSync(BaseSync):
    def __init__(self):
        super(CourseTableSync, self).__init__()
        db = cx_Oracle.connect(ORACLE_SERVER, encoding="UTF-8", nencoding="UTF-8")  # 连接数据库
        print(db.version)
        self.offset = 300
        self.cur = db.cursor()
        self.xn = '2019-2020'
        self.xq = '1'
        manager_name = "{}-{}".format(self.xn, self.xq)
        manager_number = b64encode(manager_name)
        self.manager = CourseTableManager(name=manager_name, number=manager_number)
        self.course_map = {}
        self.space_map = {}
        self.classroom_map = {}
        self.subject_map = {}

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
        count_sql = "SELECT COUNT(*) FROM V_BZKS_JSKB WHERE XN='{}' AND XQ='{}' AND KCDM='020000001'".format(self.xn, self.xq)
        self.cur.execute(count_sql)
        try:
            total = self.cur.fetchall()[0][0]
        except (Exception,):
            total = 1
        total_page = total // self.offset if total % self.offset == 0 else total // self.offset + 1
        for index in range(total_page):
            print(">>> Get course in {}/{}".format(index + 1, total_page))
            si, ei = index * self.offset + 1, (index + 1) * self.offset
            sql = "SELECT k.KCDM, k.SKBJH, k.RKJSGH, k.ZC, k.XQJ, k.DSZ, k.JC, k.SKDD, k.r " \
                  "FROM (SELECT x.*, rownum r FROM V_BZKS_JSKB x " \
                  "WHERE XN='{}' AND XQ='{}' AND KCDM='020000001' ORDER BY KCDM) " \
                  "k WHERE k.r BETWEEN {} and {} ".format(self.xn, self.xq, si, ei)
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            for row in rows:
                subject_number = row[0]
                classroom_name = row[7] or "{}场地".format(subject_number)
                teacher_number = row[2]
                week_range = row[3]
                week, num = row[4], row[6]
                single = single_map.get(row[5], 0)
                begin_week, end_week = int(week_range.split("-")[0]), int(week_range.split("-")[-1])
                try:
                    space_name = classroom_name + week_range + num + week + str(single)
                    course_name = classroom_name + subject_number + teacher_number
                except (Exception, ) as e:
                    print(row)
                    continue
                if course_name in self.course_map:
                    course = self.course_map[course_name]
                else:
                    course_number = str(uuid.uuid4())
                    classroom_num = b64encode(classroom_name)
                    if classroom_num not in self.classroom_map:
                        self.classroom_map[classroom_num] = Classroom(number=classroom_num, name=classroom_name)
                    course = Course(number=course_number, name=course_name, teacher_number=teacher_number,
                                    classroom_number=classroom_num, subject_number=subject_number,
                                    begin_week=begin_week, end_week=end_week)
                    self.course_map[course_name] = course
                if space_name not in self.space_map:
                    positions = self.analyse_position(num, week)
                    for position in positions:
                        course.add_position(position[0], position[1], single)
                    self.space_map[space_name] = course

    def relate_student(self):
        single_map = {"单": 1, "双": 2}
        count_sql = "SELECT COUNT(*) FROM V_BZKS_XSKB WHERE XN='{}' AND XQ='{}' AND KCDM='020000001'".format(self.xn, self.xq)
        self.cur.execute(count_sql)
        try:
            total = self.cur.fetchall()[0][0]
        except (Exception,):
            total = 1
        total_page = total // self.offset if total % self.offset == 0 else total // self.offset + 1
        for index in range(total_page):
            print(">>> Related student in {}/{}".format(index + 1, total_page))
            si, ei = index * self.offset + 1, (index + 1) * self.offset
            sql = "SELECT k.KCDM, k.SKBJ, k.RKJSGH, k.ZC, k.XQJ, k.DSZ, k.JC, k.SKDD, k.XH, k.KCMC, k.r " \
                  "FROM (SELECT x.*, rownum r FROM V_BZKS_XSKB x " \
                  "WHERE XN='{}' AND XQ='{}' AND KCDM='020000001' ORDER BY KCDM) " \
                  "k WHERE k.r BETWEEN {} and {} ".format(self.xn, self.xq, si, ei)
            self.cur.execute(sql)
            rows = self.cur.fetchall()
            for row in rows:
                subject_number, subject_name = row[0], row[9]
                classroom_name = row[7] or "{}场地".format(subject_number)
                week_range = row[3]
                week, num = row[4], row[6]
                single = single_map.get(row[5], 0)
                student_number = row[8]
                try:
                    space_name = classroom_name + week_range + num + week + str(single)
                except (Exception, ):
                    print(row)
                    continue
                if not (subject_number and subject_name):
                    continue
                if subject_number not in self.subject_map:
                    f_subject_name = "{}_{}".format(subject_name, subject_number[-2:])
                    self.subject_map[subject_number] = Subject(number=subject_number, name=f_subject_name)
                course = self.space_map.get(space_name, None)
                if course:
                    course.add_student(student_number)

    def sync(self):
        self.get_course()
        self.relate_student()
        for number, course in self.course_map.items():
            self.manager.add_course(course)
        print(">>>Finish data process")
        classrooms = list(self.classroom_map.values())
        print(">>>Start upload classroom")
        self.client.create_classrooms(self.school_id, classrooms)
        print(">>>Finish upload classroom")
        subjects = list(self.subject_map.values())
        print(">>>Start upload subjects")
        self.client.create_subjects(self.school_id, subjects)
        print(">>>Finish upload subjects")
        print(">>>Start upload course table")
        self.client.create_course_table(self.school_id, self.manager)
        print(">>>Finish upload course table")
