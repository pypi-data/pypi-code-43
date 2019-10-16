import pymongo
from bson import Decimal128

from com.fw.system.red_conf import system_conf
from com.fw.base.base_dao import BaseDao
from com.fw.utils.common_utils import CommonUtils
from com.fw.base.base_exception import BaseException
from com.fw.db.query import QueryUtils, QueryLogical, Sud
from com.fw.db.page import PageUtils
from com.fw.db.update import UpdateUtils, Modifier
from com.fw.base.base_log import logger



class MongoDao(object):
    def __init__(self):
        self.init_pool()

    def init_pool(self):
        if not system_conf.has_group('environment'):
            raise BaseException("没有配置数据库环境...")
        version = system_conf.get_value('environment', 'version')

        key = 'mongo' + "_" + version

        if not system_conf.has_group(key):
            logger.warn("----------【warn】：没有配置mongo -------")
            return

        self.config = {
            'host': system_conf.get_value(key, 'host'),
            'port': int(system_conf.get_value(key, 'port')),
            'maxPoolSize': int(system_conf.get_value(key, 'maxPoolSize')),
            'minPoolSize': int(system_conf.get_value(key, 'minPoolSize')),
            'waitQueueMultiple':10,
            'waitQueueTimeoutMS':200,
            'connectTimeoutMS': 4000,
            'serverSelectionTimeoutMS':10000
        }

        try:
            self.db_name = system_conf.get_value(key, 'db')
            self.client = pymongo.MongoClient(**self.config)[self.db_name]




        except Exception as e:
            raise BaseException("-------ERROR:初始化 mongodb 数据库连接失败: ", e)
        else:
            logger.info(" -------mongo db 初始化成功 {} -------".format(self.config))


    @CommonUtils.check_param
    def save(self, dao: BaseDao, *args, **kwargs):
        '''
        保存
        :param dao:
        :return:
        '''
        collection_name = MongoDao.get_dao_collection_name(dao)
        dao._id = dao.id
        try:
            self.client[collection_name].save(dao.__dict__)
        except Exception as e:
            raise BaseException("MOGO SAVE EXCEPTION:", e)

    def insert_bacth(self, dao_list: list, *args, **kwargs):
        '''
        批量
        :param dao_list:
        :return:
        '''
        db_data = []
        if not dao_list or len(dao_list) == 0:
            raise BaseException(" THE DATA IS NONE OR IS EMPTY...")
        for dao in dao_list:
            if not isinstance(dao,BaseDao):
                raise BaseException(" THE DATA MUST IS BASE_DAO...")
            dao._id = dao.id
            db_data.append(dao.__dict__)
        collection_name = MongoDao.get_dao_collection_name(dao_list[0])

        try:
            self.client[collection_name].insert_many(db_data)
        except Exception as e:
            raise BaseException("INSERT BATCH ERROR :", e)

    @CommonUtils.check_param
    def find_by_id(self, collection_name: str, id: str, *args, **kwargs):
        try:
            return self.client[collection_name].find_one({"_id": id})
        except Exception as e:
            raise BaseException("FIND DATA BY ID ERROR:", e)

    def find_one_by_query(self, collection_name, query: QueryUtils, *args, **kwargs):
        sql, sort, page = MongoDao.get_query_mongon_sql(query)
        try:
            return self.client[collection_name].find_one(sql)
        except Exception as e:
            raise BaseException("FIND DATA BY ID ERROR:", e)

    def find_by_query(self, collection_name, query: QueryUtils, *args, **kwargs):
        sql, sort, page = MongoDao.get_query_mongon_sql(query)

        try:
            data = self.client[collection_name].find(sql, sort=sort)
            result = []

            for value in data:
                result.append(value)
            return result
        except Exception as e:
            raise BaseException("FIND DATA BY ID ERROR:", e)

    def find_by_query_and_page(self, collection_name, query: QueryUtils, *args, **kwargs):
        sql, sort, page = MongoDao.get_query_mongon_sql(query)

        try:
            count = self.client[collection_name].count(sql)
            data = self.client[collection_name].find(sql, sort=sort, skip=page["skip"], limit=page["limit"])

            result = []

            for value in data:
                result.append(value)

            return PageUtils((query.page.to_page - 1 if query.page.to_page >= 0 else 0) * query.page.page_size,
                             query.page.page_size, count, result)
        except Exception as e:
            raise BaseException("FIND DATA BY ID ERROR:", e)

    def update_by_query(self, collection_name, query: QueryUtils, update: UpdateUtils, *args, **kwargs):
        sql, sort, page = MongoDao.get_query_mongon_sql(query)
        update_sql = MongoDao.get_update_mongo_sql(update)
        try:
            return self.client[collection_name].update_many(sql,update_sql).modified_count
        except Exception as e:
            raise BaseException("UPDATE DATA ERROR:", e)


    def update_one_by_query(self, collection_name, query: QueryUtils, update: UpdateUtils, *args, **kwargs):
        sql, sort, page = MongoDao.get_query_mongon_sql(query)
        update_sql = MongoDao.get_update_mongo_sql(update)
        try:
            return self.client[collection_name].update_one(sql,update_sql).modified_count
        except Exception as e:
            raise BaseException("UPDATE DATA ERROR:", e)

    def find_one_and_update(self, collection_name, query: QueryUtils, update: UpdateUtils, *args, **kwargs):
        sql, sort, page = MongoDao.get_query_mongon_sql(query)
        update_sql = MongoDao.get_update_mongo_sql(update)
        try:
            return self.client[collection_name].find_one_and_update(sql, update_sql)
        except Exception as e:
            raise BaseException("UPDATE DATA ERROR:", e)

    @CommonUtils.check_param
    def remove_by_id(self, collection_name, id: str, *args, **kwargs):
        try:
            return self.client[collection_name].remove({"_id": id})
        except Exception as e:
            raise BaseException("DELETE DATA BY ID ERROR:", e)

    def remove_one_by_query(self, collection_name, query: QueryUtils, *args, **kwargs):
        sql, sort, page = MongoDao.get_query_mongon_sql(query)
        try:
            self.client[collection_name].aggregate()
            return self.client[collection_name].delete_one(sql)
        except Exception as e:
            raise BaseException("DELETE DATA BY QUERY ERROR:", e)

    def remove_by_query(self, collection_name, query: QueryUtils, *args, **kwargs):
        sql, sort, page = MongoDao.get_query_mongon_sql(query)
        try:
            return self.client[collection_name].remove(sql)
        except Exception as e:
            raise BaseException("DELETE DATA BY QUERY ERROR:", e)

    @staticmethod
    def get_update_mongo_sql(update:UpdateUtils):
        sql = {}
        if not update or len(update.params) == 0:
            raise BaseException("THE UPDATE PARAM MUST IS NO EMPTY")

        for update_kv in update.params:

            if update_kv.modifier == Modifier.IS:
                update_modifier = "$set"
            elif update_kv.modifier == Modifier.INC:
                update_modifier = "$inc"
            elif update_kv.modifier == Modifier.MONGO_UNSET:
                update_modifier = "$unset"
            elif update_kv.modifier == Modifier.MONGO_POP:
                update_modifier = "$pop"
            elif update_kv.modifier == Modifier.MONGO_PULL:
                update_modifier = "$pull"
            elif update_kv.modifier == Modifier.MONGO_PUSH:
                update_modifier = "$push"
            elif update_kv.modifier == Modifier.MONGO_ADD_TO_SET:
                update_modifier = "$addToSet"
            else:
                raise BaseException("NO UPDATE_MODIFIER...")

            if update_modifier not in sql.keys():
                sql[update_modifier] = {}

            sql[update_modifier][update_kv.key] = update_kv.val

        return sql


    @staticmethod
    def get_query_mongon_sql(query: QueryUtils):
        sql = {}
        if not query:
            return sql
        for criteria in query.criterias:

            key = criteria.key
            state = False

            if key == "id":
                key = "_id"

            if criteria.queryLogical == QueryLogical.IS:
                sql[key] = criteria.value
            elif criteria.queryLogical == QueryLogical.NIS:
                sql[key] = {"$ne": criteria.value}
            elif criteria.queryLogical == QueryLogical.LIKE_ALL:
                sql[key] = {"$regex": '/{}/'.format(criteria.value)}
            elif criteria.queryLogical == QueryLogical.LIKE_LEFT:
                sql[key] = {"$regex": '^{}.*'.format(criteria.value)}
            elif criteria.queryLogical == QueryLogical.LIKE_RIGHT:
                sql[key] = {"$regex": '.*{}$'.format(criteria.value)}
            elif criteria.queryLogical == QueryLogical.IN:
                if isinstance(criteria.value, list):
                    sql[key] = {"$in": criteria.value}
                else:
                    raise BaseException("QUERY IN VALUE MUST IS LIST DATA ...")
            elif criteria.queryLogical == QueryLogical.NOT_IN:
                if isinstance(criteria.value, list):
                    sql[key] = {"$nin": criteria.value}
                else:
                    raise BaseException("QUERY NOT IN VALUE MUST IS LIST DATA ...")
            elif criteria.queryLogical == QueryLogical.GT:
                state = True
                mongo_key = "$gt"
            elif criteria.queryLogical == QueryLogical.GTE:
                state = True
                mongo_key = "$gte"
            elif criteria.queryLogical == QueryLogical.LT:
                state = True
                mongo_key = "$lt"
            elif criteria.queryLogical == QueryLogical.LTE:
                state = True
                mongo_key = "$lte"
            if state:
                if key not in sql.keys():
                    sql[key] = {mongo_key: criteria.value}
                else:
                    sql[key][mongo_key] = criteria.value

        sort = None

        if query.sort:
            sort = [(query.sort.key, pymongo.ASCENDING if query.sort.sud == Sud.ASC else pymongo.DESCENDING)]

        page = {}
        page["limit"] = query.page.page_size
        page["skip"] = (query.page.to_page - 1) * query.page.page_size

        return sql, sort, page

    @staticmethod
    def get_dao_collection_name(dao: BaseDao):
        '''
        获取集合名称
        :param dao:
        :return:
        '''
        collection_name = dao.table_name
        if CommonUtils.isEmpty(collection_name):
            raise BaseException("NO SET COLLECTION...")

        return collection_name

    @staticmethod
    def get_dao_collection_name(T):
        '''
        获取集合名称
        :param dao:
        :return:
        '''
        collection_name = T.table_name
        if CommonUtils.isEmpty(collection_name):
            raise BaseException("NO SET COLLECTION...")

        return collection_name


mongo_dao = MongoDao()
