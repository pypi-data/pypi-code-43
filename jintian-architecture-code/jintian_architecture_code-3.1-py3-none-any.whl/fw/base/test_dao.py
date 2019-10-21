from com.fw.base.base_dao import BaseDao
from com.fw.utils.id_util import IDUtils


class TestDao(BaseDao):
    table_name = "CRM_USER"

    def __init__(self, user_name="", pass_word="", **kwargs):
        BaseDao.__init__(self,**kwargs)
        self.user_name = user_name
        self.pass_word = pass_word
