from ..requester.nirvana import NirvanaRequester
from ..requester.edtech import EDTechRequester
from ..models.news import TypeSet
from ..settings import CLASS_CARD_SERVER_URL, EDTECH_SERVER_URL


class Backbone(object):
    course_manager = None  # CourseManager Model
    rest_table = None  # RestTable Model
    courses = {}  # num -> Course Model
    subjects = {}  # num -> Subject Model
    classrooms = {}  # num -> Classroom Model
    sections = {}  # num -> Section Model
    teachers = {}  # number -> Teacher Model
    students = {}  # number -> Student Model
    course_map = {}  # num -> uid
    subject_map = {}  # num -> uid
    classroom_map = {}  # num -> uid
    teacher_map = {}  # number -> uid
    student_map = {}  # number -> uid
    class_map = {}  # name -> uid
    album_map = {}  # name-category -> uid

    def __init__(self, school_id):
        self.nirvana_requester = NirvanaRequester(server=CLASS_CARD_SERVER_URL, school_id=school_id)
        self.edtech_requester = EDTechRequester(server=EDTECH_SERVER_URL, school_id=school_id)

    def wrap_course_map(self):
        """
        拉取班牌后台课程(教学班)列表，映射出课程uid
        :return:
        """
        self.course_map = self.nirvana_requester.wrap_map("get_course_list", ["num"], "uid", limit=0)

    def wrap_subject_map(self):
        """
        拉取班牌后台科目列表，映射出科目uid
        :return:
        """
        self.subject_map = self.nirvana_requester.wrap_map("get_subject_list", ["num"], "uid")

    def wrap_classroom_map(self):
        """
        拉取班牌后台教室列表，映射出教室uid
        :return:
        """
        self.classroom_map = self.nirvana_requester.wrap_map("get_classroom_list", ["num"], "uid")

    def wrap_class_map(self):
        """
        拉取班牌后台行政班列表，映射出行政班uid
        :return:
        """
        self.class_map = self.nirvana_requester.wrap_map("get_class_list", ["name"], "uid")

    def wrap_teacher_map(self):
        """
        拉取班牌后台教师列表，映射出教师uid
        :return:
        """
        self.teacher_map = self.nirvana_requester.wrap_map("get_teacher_list", ["number"], "uid")

    def wrap_student_map(self):
        """
        拉取班牌后台学生列表，映射出学生uid
        :return:
        """
        self.student_map = self.nirvana_requester.wrap_map("get_student_list", ["number"], "uid")

    def wrap_album_map(self):
        """
        拉取班牌后台相册列表，映射出相册uid
        :return:
        """
        self.album_map = self.nirvana_requester.wrap_map("get_album_list", ["name", "category"], "uid")

    def delete_table_manager(self, manager_id):
        """
        删除整张课程表
        :param manager_id: 课程表id
        :return:
        """
        print(">>> Delete course table")
        self.nirvana_requester.delete_table_manager(manager_id)

    def get_old_course_manager(self, key='number', value=None):
        """
        获取旧的相同课程表id
        :param key:  判定相同课程表的唯一标识字段
        :param value: 唯一标识字段值
        :return:
        """
        print(">>> Get table by {}".format(key))
        if value is None:
            value = getattr(self.course_manager, key)
        param = {key: value}
        res = self.nirvana_requester.get_table_manager(param)
        data = res.get('results', None)
        manager_id = data[0]['uid'] if data else None
        return manager_id

    def create_course_manager(self, is_active=True):
        """
        创建课程表
        :param is_active: 创建完是否立即激活
        :return:
        """
        print(">>> Create Course Table Manager")
        # delete old manager
        old_manager_id = self.get_old_course_manager()
        if old_manager_id:
            self.delete_table_manager(old_manager_id)

        # create new manager
        manager_data = self.course_manager.nirvana_data
        manager = self.nirvana_requester.create_table_manager(manager_data)
        self.course_manager.uid = manager["uid"]
        manager_mode = {"course_manager_id": self.course_manager.uid, "is_walking": self.course_manager.is_walking}
        self.nirvana_requester.set_manager_mode(manager_mode)

        # active new manager
        if is_active:
            self.nirvana_requester.active_table_manager(self.course_manager.uid)

    def create_courses(self):
        """
        创建课程(教学班)，需要通过course_manager
        该创建不包含课程表的课位
        :return:
        """
        print(">>> Batch Create Course")
        batch_data = {"manager": self.course_manager.uid, "item": []}
        index, total = 0, len(self.course_manager.courses)
        for course in self.course_manager.courses:
            course.is_walking = self.course_manager.is_walking
            batch_data["item"].append(course.nirvana_data)
            if len(batch_data["item"]) >= 50:
                index += len(batch_data["item"])
                self.nirvana_requester.batch_create_course(batch_data)
                batch_data["item"] = []
                print(">>> Already create {} courses, total {}".format(index, total))
        if batch_data["item"]:
            self.nirvana_requester.batch_create_course(batch_data)
            print(">>> Already create {} courses, total {}".format(index + len(batch_data["item"]), total))

    def create_table(self):
        """
        创建课程表上的课位
        :return:
        """
        print(">>>Create Course Table")
        index, total = 0, len(self.course_manager.courses)
        for course in self.course_manager.courses:
            index += 1
            for position in course.schedule:
                table_data = {"course": {"uid": course.uid or self.course_map[str(course.number)]},
                              "manager": {"uid": self.course_manager.uid},
                              "num": position[0], "week": position[1],
                              "category": position[2]}
                self.nirvana_requester.set_course_position(table_data)
            print("##### already create {}/{} course position ####".format(index, total))

    def create_subjects(self, subjects):
        """
        同步科目信息
        :return:
        """
        print(">>>Create Subject")
        index = 0
        for subject in subjects:
            index += 1
            subject_id = self.subject_map.get(str(subject.number), None)
            if subject_id:
                res_data = self.nirvana_requester.update_subject(subject_id, subject.nirvana_data)
                subject.uid = subject_id
            else:
                print(">>>Create Subject {}/{}".format(subject.number, subject.name))
                res_data = self.nirvana_requester.create_subject(subject.nirvana_data)
                subject.uid = res_data['uid']
            print("##### already create {} {}/{} subject ####".format(subject.name, index, len(subjects)))

    def create_news(self, news):
        """
        同步新闻信息
        :param news:
        :return:
        """
        print(">>>Create News")
        news.class_id = self.class_map.get(news.class_name, None)
        if news.category == TypeSet.SCHOOL_TYPE:
            for classroom_number in news.classroom_numbers:
                if classroom_number not in self.classroom_map:
                    raise KeyError("classroom_number should be correct!")
                news.classroom_ids.append(self.classroom_map.get(classroom_number))
        res_data = self.nirvana_requester.create_news(news.nirvana_data)
        news.uid = res_data['uid']
        if news.category == TypeSet.SCHOOL_TYPE:
            self.nirvana_requester.modify_classroom_news({"news": news.uid, "ids": [news.classroom_ids]})

    def create_notice(self, notice):
        """
        同步通知信息
        :param notice: Notice
        :return:
        """
        print(">>>Create Notice")
        notice.class_id = self.class_map.get(notice.class_name, None)
        if notice.category == TypeSet.SCHOOL_TYPE:
            for classroom_number in notice.classroom_numbers:
                if classroom_number not in self.classroom_map:
                    raise KeyError("classroom_number should be correct!")
                notice.classroom_ids.append(self.classroom_map.get(classroom_number))
        res_data = self.nirvana_requester.create_broad(notice.nirvana_data)
        notice.uid = res_data['uid']
        if notice.category == TypeSet.SCHOOL_TYPE:
            self.nirvana_requester.modify_classroom_broad({"broad": notice.uid, "ids": [notice.classroom_ids]})

    def create_video(self, video):
        """
        同步视频信息
        :param video: Video
        :return:
        """
        print(">>>Create Video")
        video.class_id = self.class_map.get(video.class_name, None)
        if video.category == TypeSet.SCHOOL_TYPE:
            for classroom_number in video.classroom_numbers:
                if classroom_number not in self.classroom_map:
                    raise KeyError("classroom_number should be correct!")
                video.classroom_ids.append(self.classroom_map.get(classroom_number))
        res_data = self.nirvana_requester.create_video(video.nirvana_data)
        video.uid = res_data['uid']
        if video.category == TypeSet.SCHOOL_TYPE:
            self.nirvana_requester.modify_classroom_video({"video": video.uid, "ids": [video.classroom_ids]})

    def create_album(self, album):
        """
        同步相册信息
        :param album: Album
        :return:
        """
        print(">>>Create Album")
        key = "{}-{}".format(album.name, album.category)
        album_id = self.album_map.get(key, None)
        album.class_id = self.class_map.get(album.class_name, None)
        if album.category == TypeSet.SCHOOL_TYPE:
            for classroom_number in album.classroom_numbers:
                if classroom_number not in self.classroom_map:
                    raise KeyError("classroom_number should be correct!")
                album.classroom_ids.append(self.classroom_map.get(classroom_number))
        if album_id:
            res_data = self.nirvana_requester.update_album(album_id, album.nirvana_data)
        else:
            res_data = self.nirvana_requester.create_album(album.nirvana_data)
        album.uid = res_data['uid']
        if album.category == TypeSet.SCHOOL_TYPE:
            self.nirvana_requester.modify_classroom_album({"album": album.uid, "ids": [album.classroom_ids]})

    def create_image(self, images, album_id):
        """
        同步图片信息
        :param images: [Image, Image]
        :param album_id:
        :return:
        """
        for image in images:
            image.album_id = album_id
        data = [img.nirvana_data for img in images]
        self.nirvana_requester.create_image(data)

    def arrange_images(self, images):
        """
        整理图片信息，把同一个相册的放在一起
        :param images: [Image, Image]
        :return:
        """
        img_set = {}
        for img in images:
            key = "{}-{}".format(img.album_name, img.album_category)
            album_id = self.album_map[key]
            if album_id not in img_set:
                img_set[album_id] = []
            img_set[album_id].append(img)
        return img_set

    def create_classrooms(self, classrooms):
        """
        同步教室信息
        :return:
        """
        print(">>>Create Classroom")
        index = 0
        for classroom in classrooms:
            index += 1
            classroom_id = self.classroom_map.get(str(classroom.number), None)
            if classroom_id:
                res_data = self.nirvana_requester.update_classroom(classroom_id, classroom.nirvana_data)
                classroom.uid = classroom_id
            else:
                res_data = self.nirvana_requester.create_classroom(classroom.nirvana_data)
                classroom.uid = res_data['uid']
            print("##### already create {} {}/{} classroom ####".format(classroom.name, index, len(classrooms)))

    def relate_course_field(self):
        """
        将模型Course中的字段通过映射，转换为uid。(班牌后台接口结构)
        :return:
        """
        for course in self.course_manager.courses:
            course.subject_id = self.subject_map.get(str(course.subject_number), None)
            if not course.subject_id:
                print(">>>ERROR: subject_number{}错误，无法找到对应的科目".format(course.subject_number))
            course.classroom_id = self.classroom_map.get(str(course.classroom_number), None)
            course.teacher_id = self.teacher_map.get(course.teacher_number, None)
            course.class_id = self.class_map.get(course.class_name, None)
            for student_number in course.student_list:
                student_id = self.student_map.get(student_number, None)
                if not student_id:
                    print(">>>ERROR: student_number{}错误，无法找到对应的学生".format(student_number))
                course.student_ids.append(student_id)

    def get_old_rest_table(self, key='number', value=None):
        """
        获取旧的相同作息表id
        :param key:  判定相同作息表的唯一标识字段
        :param value: 唯一标识字段值
        :return:
        """
        print(">>> Get table by {}".format(key))
        if value is None:
            value = getattr(self.rest_table, key)
        param = {key: value}
        res = self.nirvana_requester.get_rest_table(param)
        data = res.get('results', None)
        rest_table_id = data[0]['uid'] if data else None
        return rest_table_id

    def create_rest_table(self, is_active=False):
        """
        创建作息表
        :param is_active: 创建好作息表后是否立即激活，不建议立即激活
        :return:
        """
        # delete old rest table
        old_rest_table_id = self.get_old_rest_table()
        if old_rest_table_id:
            self.delete_rest_table(old_rest_table_id)

        upload_data = self.rest_table.nirvana_data
        res_data = self.nirvana_requester.create_rest_table(upload_data)
        self.rest_table.uid = res_data['uid']

        if is_active:
            self.nirvana_requester.active_rest_table(res_data['uid'])

    def delete_rest_table(self, rest_table_id):
        """
        删除作息表
        :param rest_table_id:
        :return:
        """
        print(">>> Delete rest table")
        self.nirvana_requester.delete_rest_table(rest_table_id)

    def upload_rest_table(self, rest_table=None, is_active=False):
        """
        用于client调用，创建作息表
        :param rest_table: instance of RestTable for create
        :param is_active: 创建好作息表后是否立即激活，不建议立即激活
        :return:
        """
        self.rest_table = rest_table or self.rest_table
        self.create_rest_table(is_active)

    def upload_course_table(self, course_manager=None, is_active=False):
        """
        用于client调用，创建课程表
        :param course_manager: instance of CourseTableManager for create
        :param is_active: 创建好课程表后是否立即激活，不建议立即激活
        :return:
        """
        self.course_manager = course_manager or self.course_manager
        self.wrap_subject_map()
        self.wrap_classroom_map()
        self.wrap_teacher_map()
        self.wrap_class_map()
        self.wrap_student_map()
        self.relate_course_field()
        self.create_course_manager(is_active)
        self.create_courses()
        self.wrap_course_map()
        self.create_table()

    def upload_subjects(self, subjects):
        """
        用于client调用，创建科目
        :param subjects: [Subject, Subject]
        :return:
        """
        self.wrap_subject_map()
        self.create_subjects(subjects)

    def upload_classrooms(self, classrooms):
        """
        用于client调用，创建教室
        :param classrooms: [Classroom, Classroom]
        :return:
        """
        self.wrap_classroom_map()
        self.create_classrooms(classrooms)

    def upload_news(self, news):
        """
        用于client调用，创建新闻
        :param news: News
        :return:
        """
        if news.category == TypeSet.CLASS_TYPE:
            self.wrap_class_map()
        elif news.category == TypeSet.SCHOOL_TYPE:
            self.wrap_classroom_map()
        self.create_news(news)

    def upload_notice(self, notice):
        """
        用于client调用，创建通知
        :param notice: Notice
        :return:
        """
        if notice.category == TypeSet.CLASS_TYPE:
            self.wrap_class_map()
        elif notice.category == TypeSet.SCHOOL_TYPE:
            self.wrap_classroom_map()
        self.create_notice(notice)

    def upload_video(self, video):
        """
        用于client调用，创建视频
        :param video: Video
        :return:
        """
        if video.category == TypeSet.CLASS_TYPE:
            self.wrap_class_map()
        elif video.category == TypeSet.SCHOOL_TYPE:
            self.wrap_classroom_map()
        self.create_video(video)

    def upload_album(self, album):
        """
        用于client调用，创建相册
        :param album: Album
        :return:
        """
        self.wrap_album_map()
        if album.category == TypeSet.CLASS_TYPE:
            self.wrap_class_map()
        elif album.category == TypeSet.SCHOOL_TYPE:
            self.wrap_classroom_map()
        self.create_album(album)
        self.create_image(album.images, album.uid)

    def upload_image(self, images):
        """
        用于client调用，创建相册
        :param images: [Image, Image, Image]
        :return:
        """
        self.wrap_album_map()
        img_set = self.arrange_images(images)
        for album_id, imgs in img_set.items():
            self.create_image(imgs, album_id)
