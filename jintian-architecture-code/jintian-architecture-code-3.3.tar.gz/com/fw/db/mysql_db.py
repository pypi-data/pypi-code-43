"""
数据库连接工具类
# """
import pymysql
from DBUtils.PooledDB import PooledDB

from com.fw.base.base_dao import BaseDao
from com.fw.base.base_exception import BaseException
from com.fw.base.base_log import logger
from com.fw.base.test_dao import TestDao
from com.fw.db.page import PageUtils
from com.fw.db.query import QueryUtils, QueryLogical, Page
from com.fw.db.update import UpdateUtils, Modifier
from com.fw.system.red_conf import system_conf
from com.fw.utils.enums_utils import ClassType
from com.fw.utils.id_util import IDUtils


class MysqlDao(object):
    def __init__(self):
        self.init_pool()

    def init_pool(self):

        if not system_conf.has_group('environment'):
            raise BaseException("没有配置数据库环境...")

        version = system_conf.get_value('environment', 'version')

        key = 'mysql' + "_" + version

        if not system_conf.has_group(key):
            logger.warn("-----WARN：没有配置mysql -------")
            return

        self.config = {
            'host': system_conf.get_value(key, 'host'),
            'user': system_conf.get_value(key, 'user'),
            'passwd': system_conf.get_value(key, 'passwd'),
            'db': system_conf.get_value(key, 'db'),
            'port': int(system_conf.get_value(key, 'port'))
        }

        try:
            # 以单线程的方式初始化数据库连接池
            self.pool = PooledDB(creator=pymysql,
                                 mincached=int(system_conf.get_value(key, 'mincached')),
                                 maxcached=int(system_conf.get_value(key, 'maxcached')),
                                 maxconnections=int(system_conf.get_value(key, 'maxconnections')),
                                 blocking=system_conf.get_value(key, 'blocking'), maxusage=0,
                                 setsession=['SET AUTOCOMMIT = 1'],
                                 **self.config)

        except Exception as  e:
            raise BaseException("-------ERROR:初始化mysql数据库连接失败: ", e)
        else:
            logger.info(" -------mysql 初始化成功 {} -------".format(self.config))

    def get_and_start_transaction(self):
        '''
        获取一个事务连接
        :return:
        '''
        conn = self.pool.connection()
        conn.begin()
        cursor = conn.cursor()
        return conn, cursor

    def get_conn(self, sql, **kwargs):

        if not sql:
            raise BaseException("THE SQL IS NONE ...")

        if "t_conn" not in kwargs.keys():
            conn = self.pool.connection()
            cursor = conn.cursor()
        else:
            cursor = kwargs["t_conn"]

        try:
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
        except Exception as err:
            raise BaseException("mysql exec error", err)
        finally:
            if "t_conn" not in kwargs.keys():
                conn.commit()
                cursor.close()
                conn.close()

    def get_conns(self, sqls, **kwargs):

        if not sqls:
            raise BaseException("THE SQL IS NONE ...")

        if "t_conn" not in kwargs.keys():
            conn = self.pool.connection()
            cursor = conn.cursor()
        else:
            cursor = kwargs["t_conn"]
        count = 0
        try:
            for sql in sqls:
                count += cursor.execute(sql)
            return count
        except Exception as err:
            raise BaseException("mysql exec error", err)
        finally:
            if "t_conn" not in kwargs.keys():
                conn.commit()
                cursor.close()
                conn.close()

    def insert(self, dao: BaseDao, **kwargs):
        self.save_dao(dao, "INSERT", **kwargs)

    def insert_batch(self, T: BaseDao, daos, **kwargs):
        self.save_daos(T, daos, "INSERT", **kwargs)

    def delete_by_id(self, T: BaseDao, id: str, **kwargs):
        table_name = T.table_name
        sql = 'DELETE FROM `%s` WHERE ID = "%s"' % (table_name, id)
        try:
            self.get_conn(sql, **kwargs)
        except BaseException as err:
            raise BaseException("【DELETE ERROR】", err)

    def find_by_id(self, T: BaseDao, id: str, **kwargs):
        query = QueryUtils()
        query.add_criteria("id", id, QueryLogical.IS)
        data = self.exec_query(T, query, **kwargs)
        return data[0] if len(data) > 0 else None

    def find_all(self, T: BaseDao, **kwargs):
        return self.exec_query(T, **kwargs)

    def find_one_by_query(self, T: BaseDao, query: QueryUtils = None, **kwargs):
        result = self.exec_query(T, query, **kwargs)
        return None if len(result) == 0 else result[0]

    def exec_query_sql_page(self, T, sql, page: Page, **kwargs):

        count_sql = "SELECT COUNT(*) FROM ({}) ".format(sql)

        count = self.exec(None, count_sql, **kwargs)[0]

        query_sql = "SELECT * FROM ({}) ".format(sql) + MysqlDao.generate_page_sql_by_page(page)

        data = self.exec(T, query_sql, **kwargs)

        return PageUtils((page.to_page - 1 if page.to_page >= 0 else 0) * page.page_size,
                         page.page_size, count,
                         [] if not data else (data if isinstance(data, list) else [data]))

    def exec_query_page(self, T: BaseDao, query: QueryUtils = None, **kwargs):
        if not T:
            raise BaseException("【QUERY ERROR】NO SQL OR RESULT CLASS ...")

        count_sql = MysqlDao.generate_count_sql(T) + MysqlDao.generate_query_sql(query)

        count = self.exec(None, count_sql, **kwargs)[0]

        query_sql = MysqlDao.generate_select_sql(T) + MysqlDao.generate_query_sql(query) + MysqlDao.generate_page_sql(
            query)

        data = self.exec(T, query_sql, **kwargs)

        return PageUtils((query.page.to_page - 1 if query.page.to_page >= 0 else 0) * query.page.page_size,
                         query.page.page_size, count,
                         [] if not data else (data if isinstance(data, list) else [data]))

    def exec_query(self, T: BaseDao, query: QueryUtils = None, **kwargs):

        '''
        mysql select 操作
        :param sql: sql语句
        :return: 查询结果
        '''

        if not T:
            raise BaseException("【QUERY ERROR】NO SQL OR RESULT CLASS ...")

        sql = MysqlDao.generate_select_sql(T) + MysqlDao.generate_query_sql(query)

        data = self.exec(T, sql, **kwargs)

        return [] if not data else (data if isinstance(data, list) else [data])

    def exec(self, T, sql, **kwargs):
        '''
        执行指定sql
        :param T:
        :param sql:
        :return:
        '''
        try:
            resultList = list(self.get_conn(sql, **kwargs))
            daoList = []

            if not T:
                daoList = resultList
            else:

                if issubclass(T, BaseDao):
                    if "dao_fileds" in kwargs.keys():
                        dao_fileds = kwargs["dao_fileds"]
                    else:
                        dao_fileds = BaseDao.get_dao_fileds(T)

                for result in resultList:

                    if T == ClassType.STR.name:
                        daoList.append(str(result))
                    elif T == ClassType.INT.name:
                        daoList.append(int(result))
                        daoList.append(int(result))
                    elif T == ClassType.FLOAT.name:
                        daoList.append(float(result))
                    elif T == ClassType.BOOLEAN.name:
                        daoList.append(True if str(result) == "true" or str(result) == "TRUE" else False)
                    elif issubclass(T, BaseDao):
                        params = {}
                        id = None
                        for i, key in enumerate(dao_fileds):
                            if key == "id":
                                id = result[i]
                                continue
                            params[key] = result[i]
                        dao = T(**params)
                        if id:
                            dao.set_value("id", id)
                        daoList.append(dao)
                    else:
                        raise BaseException("未知数据类型...")

            if len(daoList) == 0:
                return None
            elif len(daoList) == 1:
                return daoList[0]
            else:
                return daoList

        except BaseException as err:
            raise BaseException("【QUERY ERROR】", err)

    def save_daos(self, T: BaseDao, daos, type="REPLACE", **kwargs):
        '''
        保存
        :param dao:
        :return:
        '''
        if not daos or len(daos) == 0:
            raise BaseException("缺少必要参数...")

        table_name = T.table_name

        sqls = []

        for dao in daos:
            columns = list()
            values = list()
            columns.append(table_name.upper())

            sql_start = type + " INTO `{}` ( "
            sql_end = " ) VALUES ( "

            for (k, v) in dao.__dict__.items():
                if k == "table_name":
                    continue
                if None != v:
                    sql_start += '`{}`,'
                    sql_end += '"{}",'
                    columns.append(k.upper())
                    values.append(v)

            sql_start = sql_start[:-1]
            sql_end = sql_end[:-1]

            sql_start = sql_start.format(*columns)
            sql_end = sql_end.format(*values)

            sql = sql_start + sql_end + " )";

            sqls.append(sql)

        if len(sqls > 500):
            count = 0
            start = 0
            batch_size = 500
            num = 1
            while start < len(sqls):

                end = start + batch_size

                if end > len(sqls):
                    end = len(sqls)

                try:
                    logger.info("正在执行第{}个批量".format(num))
                    count += self.get_conns(sqls[start:end], **kwargs)
                except BaseException as err:
                    logger.exception("批量插入出错...", err)
                    continue
                finally:
                    num += 1
                    start += batch_size
            return count
        else:
            try:
                return self.get_conns(sqls, **kwargs)
            except BaseException as err:
                raise BaseException("【" + type + " ERROR】", err)

    def save_dao(self, dao: BaseDao, type="REPLACE", **kwargs):
        '''
        保存
        :param dao:
        :return:
        '''
        if not dao or not dao.__dict__["id"] or len(dao.get_keys()) <= 1:
            raise BaseException("缺少必要参数...")

        table_name = dao.table_name

        columns = list()
        values = list()
        columns.append(table_name.upper())

        sql_start = type + " INTO `{}` ( "
        sql_end = " ) VALUES ( "

        for (k, v) in dao.__dict__.items():
            if k == "table_name":
                continue
            if None != v:
                sql_start += '`{}`,'
                sql_end += '"{}",'
                columns.append(k.upper())
                values.append(v)

        sql_start = sql_start[:-1]
        sql_end = sql_end[:-1]

        sql_start = sql_start.format(*columns)
        sql_end = sql_end.format(*values)

        sql = sql_start + sql_end + " )";

        try:
            self.get_conn(sql, **kwargs)
        except BaseException as err:
            raise BaseException("【" + type + " ERROR】", err)

    def update_dao(self, dao: BaseDao, **kwargs):
        '''
        修改指定参数
        :param dao:
        :return:
        '''
        if not dao or not dao.__dict__["id"] or len(dao.get_keys()) <= 1:
            raise BaseException("缺少必要参数...")

        update = UpdateUtils()

        for key, val in dao.__dict__.items():
            if key == 'id' or key == 'ID' or key == "table_name":
                continue
            if val != None:
                update.add_update(key, val)

        if len(update.params.keys()) == 0:
            raise BaseException("UPDATE ALL NONE...")

        query = QueryUtils()
        query.add_criteria("ID", QueryLogical.IS, dao.get_value("id"))

        self.update_table(dao.table_name, update, query, **kwargs)

    def update_query(self, T: BaseDao, update: UpdateUtils, query: QueryUtils, **kwargs):
        return self.update_table(T.table_name, update, query, **kwargs)

    def update_table(self, table_name: str, update: UpdateUtils, query: QueryUtils, **kwargs):
        if not update or not table_name:
            raise BaseException("缺少必要参数...")
        sql = MysqlDao.generate_update_sql(table_name, update) + MysqlDao.generate_query_sql(query)

        return self.exec(None, sql, **kwargs)

    def delete(self, table_name: str, query: QueryUtils, **kwargs):
        '''
        删除操作
        :param table_name:
        :param query:
        :return:
        '''
        if not table_name or not query or len(query.criterias) <= 0:
            raise BaseException("缺少必要参数...")

        sql = " DELETE FROM `{}` ".format(table_name)
        sql += MysqlDao.generate_query_sql(query)

        return self.exec(None, sql, **kwargs)

    @staticmethod
    def generate_update_sql(table_name: str, update: UpdateUtils):
        '''
        生成update sql
        :param T:
        :return:
        '''
        values = []
        sql = "UPDATE `{}` SET "

        values.append(table_name.upper())

        for update_kv in update.params:
            if update_kv.modifier == Modifier.IS:
                sql += ' `{}` = "{}" ,'
                values.append(update_kv.key.upper())
                values.append(update_kv.val)
            elif update_kv.modifier == Modifier.INC:
                sql += ' `{}` = `{}` + {} ,'
                values.append(update_kv.key.upper())
                values.append(update_kv.key.upper())
                values.append(update_kv.val)
            else:
                raise BaseException("未知的操作符...")

        sql = sql[:-1]

        sql = sql.format(*values)

        return sql

    @staticmethod
    def generate_count_sql(T: BaseDao):
        '''
                生成sql select语句
                :param T:
                :param query:
                :return:
                '''

        table_name = T.table_name

        sql = "SELECT COUNT(*) FROM `{}` ".format(table_name)

        return sql

    @staticmethod
    def generate_page_sql(query: QueryUtils):
        sql = " LIMIT {},{} ".format((query.page.to_page - 1 if query.page.to_page >= 0 else 0) * query.page.page_size,
                                     query.page.page_size)

        return sql

    @staticmethod
    def generate_page_sql_by_page(page: Page):
        sql = " LIMIT {},{} ".format((page.to_page - 1 if page.to_page >= 0 else 0) * page.page_size,
                                     page.page_size)

        return sql

    @staticmethod
    def generate_select_sql(T: BaseDao):
        '''
                生成sql select语句
                :param T:
                :param query:
                :return:
                '''

        table_name = T.table_name
        keys = BaseDao.get_dao_fileds(T)

        sql = "SELECT "

        for i, val in enumerate(keys):
            sql += '`' + val.upper() + "`,"

        sql = sql[:-1]

        sql += " FROM `{}` ".format(table_name)

        return sql

    @staticmethod
    def generate_query_sql(query: QueryUtils):

        '''
        生成where 语句
        :param query:
        :return:
        '''

        sql = ' WHERE 1=1 '

        values = []

        if query:

            for i, criteria in enumerate(query.criterias):
                key = criteria.key
                value = criteria.value
                values.append(value)
                queryLogical = criteria.queryLogical

                sql += " AND `" + key.upper() + "` ";

                if queryLogical == QueryLogical.IS:
                    sql += ' = "{}" '
                elif queryLogical == QueryLogical.NIS:
                    sql += ' != "{}" '
                elif queryLogical == QueryLogical.LIKE_ALL:
                    sql += ' LIKE "%{}%" '
                elif queryLogical == QueryLogical.LIKE_LEFT:
                    sql += ' LIKE "{}%" '
                elif queryLogical == QueryLogical.LIKE_RIGHT:
                    sql += ' LIKE "%{}" '
                elif queryLogical == QueryLogical.IN:
                    sql += ' IN ({})'
                    del values[-1]
                    values.append(MysqlDao.get_sql_in_str(value))
                elif queryLogical == QueryLogical.NOT_IN:
                    sql += ' NOT IN ({})'
                    del values[-1]
                    values.append(MysqlDao.get_sql_in_str(value))
                elif queryLogical == QueryLogical.GT:
                    if isinstance(criteria.value, str):
                        sql += ' > "{}" '
                    else:
                        sql += ' > {} '
                elif queryLogical == QueryLogical.GTE:
                    if isinstance(criteria.value, str):
                        sql += ' >= "{}" '
                    else:
                        sql += ' >= {} '
                elif queryLogical == QueryLogical.LT:
                    if isinstance(criteria.value, str):
                        sql += ' < "{}" '
                    else:
                        sql += ' < {} '

                elif queryLogical == QueryLogical.LTE:
                    if isinstance(criteria.value, str):
                        sql += ' <= "{}" '
                    else:
                        sql += ' <= {} '

            sql = sql.format(*values);

            if query.sort:
                sql += ' ORDER BY {} {} '.format(query.sort.key.upper(), query.sort.sud.name)

        return sql

    @staticmethod
    def get_sql_in_str(data):

        if isinstance(data, list):
            param = ''
            for i, val in enumerate(data):
                param += '"{}",'

            param = param[:-1]
            return param.format(*data)
        else:
            return data


mysql_dao = MysqlDao()


def Transaction(func):
    '''
    事务装饰器
    :param func:
    :return:
    '''

    def start_transaction(*args, **kwargs):

        self = args[0]
        conn, cursor = self.system.mysql_dao.get_and_start_transaction()
        req_id = IDUtils.get_primary_key(prefix="req_id:")

        kwargs["t_conn"] = cursor

        logger.info("TRANSACTION START:" + req_id + " --------")

        try:
            result = func(*args, **kwargs)
        except BaseException as e:
            conn.rollback()
            raise e
        except Exception as e:
            conn.rollback()
            raise BaseException("TRANSACTION :" + req_id + " ROLL BACK:", e)
        else:
            logger.info("TRANSACTION COMMIT :" + req_id + " --------")
            conn.commit()

            cursor.close()
            conn.close()

            return result

    return start_transaction


if __name__ == "__main__":
    query = QueryUtils()
    query.add_page(1, 10)
    result = mysql_dao.exec_query_page(TestDao, query)
    print(result)
