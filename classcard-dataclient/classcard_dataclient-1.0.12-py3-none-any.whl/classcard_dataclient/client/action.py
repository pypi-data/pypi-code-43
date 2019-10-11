# -*- coding: utf-8 -*-
"""
Created By Murray(m18527) on 2019/9/4 16:48
"""
from .backbone import Backbone
from ..models import Teacher, Student, Class, Classroom, Subject, CourseTableManager, RestTable, News, Notice, Album, \
    Video, Image
from ..utils.constants import ERROR_PARAMS, SUCCESS, MSG
from ..utils.core import config
from ..utils.data_req import (
    create_teacher_req, create_student_req, create_section_req, get_device_info, get_section_by_school,
    get_school_by_id, get_school_by_name, create_classroom_req, create_subject_req)
from ..utils.loggerutils import logging

logger = logging.getLogger(__name__)


class DataClient(object):
    """Data client as data transfer be used for saving data to class card server"""

    def __init__(self, config_module=None):
        """
        init DataClient
        :param config_module: config module
        """
        if config_module:
            try:
                config.from_obj(config_module)
            except Exception as e:
                logger.error("Error: set config fail, Detail: {}".format(e))

    @staticmethod
    def set_config_module(module):
        try:
            config.from_obj(module)
        except Exception as e:
            logger.error("Error: set config fail, Detail: {}".format(e))

    @staticmethod
    def create_teacher(teachers):
        """
        create teacher of edtech user server.
        :param teachers:  teacher list or instance
        :return: code, msg
        """
        is_multi = True
        if not isinstance(teachers, Teacher) and not isinstance(teachers, list):
            logger.error("Error: No data or wrong teacher instance type.")
            return ERROR_PARAMS, "数据为空或格式不正确。"
        if isinstance(teachers, Teacher):
            teachers = [teachers]
            is_multi = False

        code_list, msg_list = [], []
        for t in teachers:
            code, rlt = create_teacher_req(t.sso_data, school_id=t.school)
            if code:
                logger.error("Error, create teacher fail, Detail: {}, Data: {}".format(rlt, t.sso_data))
            code_list.append(code)
            msg_list.append(rlt)

        if is_multi:
            return code_list, msg_list
        return code_list[0], msg_list[0]

    @staticmethod
    def create_student(students):
        """
        create student of edtech user server.
        :param students:  student list or instance
        :return: code, msg
        """
        is_multi = True
        if not isinstance(students, Student) and not isinstance(students, list):
            logger.error("Error: No data or wrong student instance.")
            return ERROR_PARAMS, "数据为空或格式不正确。"
        if isinstance(students, Student):
            students = [students]
            is_multi = False

        code_list, msg_list = [], []
        for s in students:
            code, rlt = create_student_req(s.sso_data, school_id=s.school)
            if code:
                logger.error("Error, create student fail, Detail: {}, Data: {}".format(rlt, s.sso_data))
            code_list.append(code)
            msg_list.append(rlt)

        if is_multi:
            return code_list, msg_list
        return code_list[0], msg_list[0]

    @staticmethod
    def create_section(sections):
        """
        create section of edtech user server.
        :param sections:  section list or instance
        :return: code, msg
        """
        is_multi = True
        if not isinstance(sections, Class) and not isinstance(sections, list):
            logger.error("Error: No data or wrong Class type.")
            return ERROR_PARAMS, "数据为空或格式不正确。"
        if isinstance(sections, Class):
            sections = [sections]
            is_multi = False

        code_list, msg_list = [], []
        for d in sections:
            code, rlt = create_section_req(d.sso_data, school_id=d.school)
            if code:
                logger.error("Error, create section fail, Detail: {}, Data: {}".format(rlt, d.sso_data))
            code_list.append(code)
            msg_list.append(rlt)

        if is_multi:
            return code_list, msg_list
        return code_list[0], msg_list[0]

    @staticmethod
    def get_class_device_info(school_id, sn):
        """get class device info"""
        code, data = get_device_info(school_id=school_id, sn=sn)
        if code:
            logger.error("Error, query class device info, Detail: {}".format(data))
        return code, data

    @staticmethod
    def get_section_list(school_id):
        """get class device info"""
        code, data = get_section_by_school(school_id=school_id)
        if code:
            logger.error("Error, query section info, Detail: {}".format(data))
        return code, data

    @staticmethod
    def get_school_by_id(school_id):
        """get school info by school_id"""
        if not school_id:
            logger.error("Error: No query params.")
            return ERROR_PARAMS, MSG[ERROR_PARAMS]

        code, data = get_school_by_id(school_id=school_id)
        if code:
            logger.error("Error, query school info fail, Detail: {}".format(data))
        return code, data

    @staticmethod
    def get_school_by_name(name):
        """get school info by school name"""
        if not name:
            logger.error("Error: No query params.")
            return ERROR_PARAMS, MSG[ERROR_PARAMS]

        code, data = get_school_by_name(name)
        if code:
            logger.error("Error, query school info fail, Detail: {}".format(data))
        return code, data

    @staticmethod
    def create_classroom(classrooms):
        """
        create classroom of class card server.
        :param classrooms:  classroom list or instance
        :return: code, msg
        """
        is_multi = True
        if not isinstance(classrooms, Classroom) and not isinstance(classrooms, list):
            logger.error("Error: No data or wrong classroom type.")
            return ERROR_PARAMS, "数据为空或格式不正确。"
        if isinstance(classrooms, Classroom):
            classrooms = [classrooms]
            is_multi = False

        code_list, msg_list = [], []
        for d in classrooms:
            code, rlt = create_classroom_req(d.nirvana_data, school_id=d.school)
            if code:
                logger.error("Error, create classroom fail, Detail: {}, Data: {}".format(rlt, d))
            code_list.append(code)
            msg_list.append(rlt if code else MSG[SUCCESS])

        if is_multi:
            return code_list, msg_list
        return code_list[0], msg_list[0]

    @staticmethod
    def create_subject(subjects):
        """
        create subject of class card server.
        :param subjects:  subject list or instance
        :return: code, msg
        """
        is_multi = True
        if not isinstance(subjects, Subject) and not isinstance(subjects, list):
            logger.error("Error: No data or wrong subject type.")
            return ERROR_PARAMS, "数据为空或格式不正确。"
        if isinstance(subjects, Subject):
            subjects = [subjects]
            is_multi = False

        code_list, msg_list = [], []
        for d in subjects:
            code, rlt = create_subject_req(d.nirvana_data, school_id=d.school)
            if code:
                logger.error("Error, create subject fail, Detail: {}, Data: {}".format(rlt, d))
            code_list.append(code)
            msg_list.append(rlt if code else MSG[SUCCESS])

        if is_multi:
            return code_list, msg_list
        return code_list[0], msg_list[0]

    @staticmethod
    def create_course_table(school_id, course_table_manager, is_active=True):
        """
        创建课程表
        :param school_id: school_id
        :param course_table_manager: Type -> models.CourseTableManager
        :param is_active: active course table right now after create it
        :return:
        """
        if not isinstance(course_table_manager, CourseTableManager):
            logger.error("TypeError: course_table_manager must be a models.CourseTableManager instance.")
            return ERROR_PARAMS, "数据类型不正确。"
        course_table_manager.validate()
        backbone = Backbone(school_id)
        backbone.upload_course_table(course_manager=course_table_manager, is_active=is_active)
        return True

    @staticmethod
    def create_rest_table(school_id, rest_table, is_active=False):
        """
        创建作息表
        :param school_id: school_id
        :param rest_table: Type -> models.RestTable
        :param is_active: active rest table right now after create it
        :return:
        """
        if not isinstance(rest_table, RestTable):
            logger.error("TypeError: rest_table must be a models.RestTable instance.")
            return ERROR_PARAMS, "数据类型不正确。"
        rest_table.validate()
        backbone = Backbone(school_id)
        backbone.upload_rest_table(rest_table=rest_table, is_active=is_active)
        return True

    @staticmethod
    def create_subjects(school_id, subjects):
        """
        同步科目
        :param school_id: school_id
        :param subjects: Type -> [models.Subject, models.Subject]
        :return:
        """
        for sub in subjects:
            if not isinstance(sub, Subject):
                logger.error("TypeError: subject must be a models.Subject instance.")
                return ERROR_PARAMS, "数据类型不正确。"
            sub.validate()
        backbone = Backbone(school_id)
        backbone.upload_subjects(subjects)
        return True

    @staticmethod
    def create_classrooms(school_id, classrooms):
        """
        同步教室
        :param school_id: school_id
        :param classrooms: Type -> [models.Classroom, models.Classroom]
        :return:
        """
        for room in classrooms:
            if not isinstance(room, Classroom):
                logger.error("TypeError: classroom must be a models.Classroom instance.")
                return ERROR_PARAMS, "数据类型不正确。"
            room.validate()
        backbone = Backbone(school_id)
        backbone.upload_classrooms(classrooms)
        return True

    @staticmethod
    def create_news(school_id, news):
        """
        同步新闻
        :param school_id: school_id
        :param news: News
        :return:
        """
        if not isinstance(news, News):
            logger.error("TypeError: news must be a models.News instance.")
            return ERROR_PARAMS, "数据类型不正确。"
        news.validate()
        backbone = Backbone(school_id)
        backbone.upload_news(news)
        return True

    @staticmethod
    def create_notice(school_id, notice):
        """
        同步通知
        :param school_id: school_id
        :param notice: Notice
        :return:
        """
        if not isinstance(notice, Notice):
            logger.error("TypeError: notice must be a models.Notice instance.")
            return ERROR_PARAMS, "数据类型不正确。"
        notice.validate()
        backbone = Backbone(school_id)
        backbone.upload_notice(notice)
        return True

    @staticmethod
    def create_video(school_id, video):
        """
        同步通知
        :param school_id: school_id
        :param video: Video
        :return:
        """
        if not isinstance(video, Video):
            logger.error("TypeError: video must be a models.Video instance.")
            return ERROR_PARAMS, "数据类型不正确。"
        video.validate()
        backbone = Backbone(school_id)
        backbone.upload_video(video)
        return True

    @staticmethod
    def create_album(school_id, album):
        """
        同步通知
        :param school_id: school_id
        :param album: Album
        :return:
        """
        if not isinstance(album, Album):
            logger.error("TypeError: album must be a models.Album instance.")
            return ERROR_PARAMS, "数据类型不正确。"
        album.validate()
        backbone = Backbone(school_id)
        backbone.upload_album(album)
        return True

    @staticmethod
    def create_image(school_id, images):
        """
        同步通知
        :param school_id: school_id
        :param images: [Image, Image]
        :return:
        """
        for img in images:
            if not isinstance(img, Image):
                logger.error("TypeError: img must be a models.Image instance.")
                return ERROR_PARAMS, "数据类型不正确。"
            img.validate()
        backbone = Backbone(school_id)
        backbone.upload_image(images)
        return True
