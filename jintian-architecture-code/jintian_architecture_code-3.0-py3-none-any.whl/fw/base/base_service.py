from com.fw.system.run import system
from com.fw.base.base_dao import BaseDao
from com.fw.base.base_exception import BaseException
from com.fw.db.query import QueryUtils



class BaseService(object):

    def __init__(self, name: str):
        self.system = system
        self.name = name


    def delete_by_id(self, T, id: str, db="mysql", **kwargs):
        if not id or id == "":
            raise BaseException("缺少必要参数")
        '''
        删除根据id
        :param id:
        :return:
        '''
        try:
            if db == "mysql":
                self.system.mysql_dao.delete_by_id(T, id, **kwargs)
            else:
                self.system.mongo_dao.remove_by_id(T.table_name, id, **kwargs)
        except Exception as e:
            raise BaseException("删除" + self.name + "数据失败:", e)

    def insert_dao(self, dao: BaseDao, db="mysql", **kwargs):
        '''
        插入数据
        :param dao:
        :return:
        '''
        try:
            if db == "mysql":
                self.system.mysql_dao.insert(dao, **kwargs)
            else:
                self.system.mongo_dao.save(dao, **kwargs)
        except Exception as e:
            raise BaseException("保存" + self.name + "失败", e)

    def select_all_data(self, T: BaseDao, db="mysql", **kwargs):
        '''
        查询全部数据
        :param T:
        :return:
        '''
        try:
            if db == "mysql":
                return self.system.mysql_dao.find_all(T, **kwargs)
            else:
                return self.system.mongo_dao.find_by_query(T.table_name, None, **kwargs)
        except Exception as e:
            raise BaseException("查询" + self.name + "数据失败", e)

    def update_dao(self, dao: BaseDao, db="mysql", **kwargs):
        '''
        修改数据
        :param dao:
        :return:
        '''

        if not dao or dao.id == None or dao.id == "":
            raise BaseException("缺少必要参数")
        try:
            if db == "mysql":
                self.system.mysql_dao.update_dao(dao, **kwargs)
            else:
                self.system.mongo_dao.save(dao, **kwargs)
        except Exception as e:
            raise BaseException("修改" + self.name + "数据失败", e)

    def load(self, T: BaseDao, id, db="mysql", **kwargs):
        '''
        根据id加载一条数据
        :param T:
        :param id:
        :return:
        '''
        if not T or id == None or id == "":
            raise BaseException("缺少必要参数")

        try:
            if db == "mysql":
                return self.system.mysql_dao.find_by_id(T, id, **kwargs)
            else:
                return self.system.mongo_dao.find_by_id(T.table_name, id, **kwargs)
        except Exception as e:
            raise BaseException("获取" + self.name + "数据失败", e)

    def query_by_page(self, T: BaseDao, query: QueryUtils, db="mysql", **kwargs):
        '''
        查询分页
        :param T:
        :param query:
        :return:
        '''
        if not T:
            raise BaseException("缺少必要参数")
        try:
            if db == "mysql":
                return self.system.mysql_dao.exec_query_page(T, query, **kwargs)
            else:
                return self.system.mongo_dao.find_by_query_and_page(T.table_name, query, **kwargs)
        except Exception as e:
            raise BaseException("查询" + self.name + "数据失败", e)
