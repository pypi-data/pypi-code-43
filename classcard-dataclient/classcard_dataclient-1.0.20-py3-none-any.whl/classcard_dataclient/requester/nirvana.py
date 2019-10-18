from ..requester import Requester
from ..settings import CLASS_CARD_SERVER_TOKEN, CLASS_CARD_SCHOOL


class NirvanaRequester(Requester):
    def __init__(self, *args, **kwargs):
        super(NirvanaRequester, self).__init__(*args, **kwargs)
        self.headers = {"X-Custom-Header-3School": kwargs.get('school_id', CLASS_CARD_SCHOOL),
                        "X-Custom-Header-3App": "classcard",
                        "Authorization": CLASS_CARD_SERVER_TOKEN}

    def check_res(self, data):
        if data['code'] != 0:
            raise ConnectionError(data['message'])
        return data['data'], True

    def get_subject_list(self, params={}):
        route = "/api/subject/"
        res = self._get_method(route, params=params)
        return res

    def get_classroom_list(self, params={}):
        route = "/api/classroom_mini/"
        res = self._get_method(route, params=params)
        return res

    def get_student_list(self, params={}):
        route = "/api/student/"
        res = self._get_method(route, params=params)
        return res

    def get_teacher_list(self, params={}):
        route = "/api/teacher_mini/"
        res = self._get_method(route, params=params)
        return res

    def get_class_list(self, params={}):
        route = "/api/class/"
        res = self._get_method(route, params=params)
        return res

    def create_table_manager(self, data):
        route = "/api/course_table_manager/"
        res = self._post_method(route, data)
        return res

    def set_manager_mode(self, data):
        route = "/api/course_walking_mode/"
        res = self._post_method(route, data)
        return res

    def set_course_position(self, data):
        route = "/api/course_table/"
        res = self._post_method(route, data)
        return res

    def batch_create_course(self, data):
        route = "/api/course_batch/"
        res = self._post_method(route, data)
        return res

    def get_course_list(self, params={}):
        route = "/api/course_list/"
        res = self._get_method(route, params=params)
        return res

    def get_table_manager(self, params):
        route = "/api/course_table_manager/"
        res = self._get_method(route, params)
        return res

    def delete_table_manager(self, uid):
        route = "/api/course_table_manager/{}/".format(uid)
        data = {"soft": False,
                "force": True}
        res = self._delete_method(route, data)
        return res

    def active_table_manager(self, uid):
        route = "/api/course_table_active/"
        data = {"uid": uid}
        res = self._post_method(route, data)
        return res

    def delete_classroom_course(self, classroom_id, manager_id):
        route = "/api/course/?classroom__uid={}&manager__uid={}".format(classroom_id, manager_id)
        res = self._delete_method(route, data={"force": True})
        return res

    def get_active_manager(self):
        route = "/api/course_table_manager/"
        res = self._get_method(route, {"is_active": "true"})
        data = res.get('results', None)
        return data[0]['uid']

    def create_classroom(self, data):
        route = "/api/classroom/"
        res = self._post_method(route, data)
        return res

    def update_classroom(self, uid, data):
        route = "/api/classroom/{}/".format(uid)
        res = self._put_method(route, data)
        return res

    def create_subject(self, data):
        route = "/api/subject/"
        res = self._post_method(route, data)
        return res

    def update_subject(self, uid, data):
        route = "/api/subject/{}/".format(uid)
        res = self._put_method(route, data)
        return res

    def get_rest_table(self, params):
        route = "/api/rest_table/"
        res = self._get_method(route, params)
        return res

    def active_rest_table(self, uid):
        route = "/api/rest_table_active/"
        data = {"uid": uid}
        res = self._post_method(route, data)
        return res

    def create_rest_table(self, data):
        route = "/api/rest_table/"
        res = self._post_method(route, data)
        return res

    def delete_rest_table(self, uid):
        route = "/api/rest_table/{}/".format(uid)
        data = {"soft": False,
                "force": True}
        res = self._delete_method(route, data)
        return res

    def create_news(self, data):
        route = "/api/news/"
        res = self._post_method(route, data)
        return res

    def create_broad(self, data):
        route = "/api/broad/"
        res = self._post_method(route, data)
        return res

    def get_album_list(self, params):
        route = "/api/album/"
        res = self._get_method(route, params)
        return res

    def create_album(self, data):
        route = "/api/album/"
        res = self._post_method(route, data)
        return res

    def update_album(self, album_id, data):
        route = "/api/album/{}/".format(album_id)
        res = self._put_method(route, data)
        return res

    def create_image(self, data):
        route = "/api/image_bat/"
        res = self._post_method(route, data)
        return res

    def create_video(self, data):
        route = "/api/video/"
        res = self._post_method(route, data)
        return res

    def modify_classroom_news(self, data):
        route = "/api/classroom_news_modify/"
        res = self._put_method(route, data)
        return res

    def modify_classroom_broad(self, data):
        route = "/api/classroom_broad_modify/"
        res = self._put_method(route, data)
        return res

    def modify_classroom_album(self, data):
        route = "/api/classroom_album_modify/"
        res = self._put_method(route, data)
        return res

    def modify_classroom_video(self, data):
        route = "/api/classroom_video_modify/"
        res = self._put_method(route, data)
        return res
