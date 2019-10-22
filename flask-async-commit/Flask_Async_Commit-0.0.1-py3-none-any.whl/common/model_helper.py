# coding: utf-8
# import threading
# import random
import time

from configs.db_config import db
from common.except_helper import DataBaseCommitError
from common.time_helper import to_int_timestamp, int_timestamp, to_formatted_time
from configs.db_config import my_cache
from collections import defaultdict
from configs.application import app
import random
import os
import copy
import gc
import sys
import gevent
# this_thread_cache_list = 'SQL-list' + str(os.getpid())
# # # running = False
# # # lock = threading.Lock()
# while True:
#     this_thread_cache_list = random.randint(0, 10000000)
#     if my_cache.sismember('SQL-list-flag-list', this_thread_cache_list):
#         continue
#     else:
#         my_cache.sadd('SQL-list-flag-list', this_thread_cache_list)
#         this_thread_cache_list = 'SQL-list' + str(this_thread_cache_list)
#         break
# print('my flag is', this_thread_cache_list)



class DictAble():
    """
    父类，使继承此类的对象可以拥有便捷的组装成为字典的能力
    并且过滤了所有的内部属性，返回一个字典
    """
    def to_dict(self):
        d = self.__dict__
        for i in list(self.__dict__.keys()):
            if '_' == i[0]:
                del d[i]
        return d


class QuickSave():
    """
    立刻保存数据，还有一个可能拥有的方法是CacheSave
    """
    def quick_save(self):
        db.session.add(self)
        try:
            db.session.commit()
        except Exception as e:
            print('sql commit error info {}'.format(str(e)))
            db.session.rollback()
            raise DataBaseCommitError('数据库提交错误, 一条记录未能提交')


my_cache.delete('CacheInfo')
my_cache.delete('SQLCachePoolReadyList')
for i in range(100):
    my_cache.delete('SQLCachePoolNo.{}'.format(i+1))
for i in range(5):
    my_cache.rpush('SQLCachePoolReadyList', 'SQLCachePoolNo.{}'.format(i+1))
class CacheSave(DictAble):
    """
        缓存并双策略执行提交

    """
    # TODO: 多个数据库的提交机制
    # TODO: SQL语句错误的回滚机制
    # TODO:
    max_package_size = 1024*1024*40

    def cache_save(self):
        # 通过再开一个线程，来提交缓存
        raw_insert_sql = self._make_insert_SQL()                # 用redis缓存原生SQL语句
        cache_pool_name = self._get_usable_cache_pool()

        self._push_sql(cache_pool_name, raw_insert_sql)
        self._incr_pool_used(cache_pool_name, len(raw_insert_sql.encode()))
        # 增加执行条件，判断长度是否到达指定要求
        if self._get_pool_used(cache_pool_name) >= self.max_package_size:
            print('我主动去了！')
            g = gevent.spawn(self.commit_db_cache)
            g.join()

    @classmethod
    def commit_db_cache(cls):
        """从model_cache中拿数据，并commit"""
        gc.collect()
        with app.app_context():
            with cls.use_cache_pool() as cache_pool_name:       # 在互斥访问这个cache pool的情况下，对其进行操作
                if cache_pool_name is None:
                    return
                time.sleep(5)
                SQLs = [x.decode() for x in my_cache.lrange(cache_pool_name, 0, -1)]

                if len(SQLs) == 0:
                    return
                print('pid ', os.getpid(), 'commit count', len(SQLs))

                SQLs = ';'.join(SQLs)
                db.session.execute(SQLs)

                # 尝试提交，并处理错误
                try:
                    db.session.commit()
                except Exception as e:
                    print('sql commit error info {}'.format(str(e)))
                    db.session.rollback()
                    raise DataBaseCommitError('数据库提交错误, %d记录未能提交' % len(SQLs))
                db.session.close()
                cls._clear_pool_used(cache_pool_name)

    """
        CacheInfo：hash，保存了每个pool已经使用的大小和pool的总数
        SQLCachePoolReadyList：pool的name的队列
        SQLCachePoolNo.N：各个池
    """
    def _get_pool_used(self, cache_pool_name):
        return int(my_cache.hget('CacheInfo', cache_pool_name + 'Used'))

    def _incr_pool_used(self, cache_pool_name, size):
        my_cache.hincrby('CacheInfo', cache_pool_name + 'Used', int(size))

    @classmethod
    def _clear_pool_used(cls, cache_pool_name):
        my_cache.hincrby('CacheInfo', cache_pool_name + 'Used', 0)

    def _push_sql(self, cache_pool_name, raw_insert_sql):
        my_cache.rpush(cache_pool_name, raw_insert_sql)

    @classmethod
    def use_cache_pool(cls):
        class cache_pool:
            def __enter__(self):
                cache_pool_name = my_cache.lpop('SQLCachePoolReadyList')
                if cache_pool_name is None:
                    self.cache_pool_name = None
                else:
                    self.cache_pool_name = cache_pool_name.decode()
                return self.cache_pool_name

            def __exit__(self, type, value, trace):
                my_cache.rpush('SQLCachePoolReadyList', self.cache_pool_name)
                my_cache.delete(self.cache_pool_name)
                my_cache.hset('CacheInfo', self.cache_pool_name + 'Used', 0)
        return cache_pool()

    def _get_usable_cache_pool(self):
        """
        从list中拿出第一个元素块，或者重新创造出一个缓存块
        :return: 缓存块的名字
        """
        if my_cache.llen('SQLCachePoolReadyList') == 0:
            cache_pool_name = self._create_cache_pool()
        else:
            cache_pool_name = my_cache.lindex('SQLCachePoolReadyList', 0)
            if cache_pool_name is None:
                return self._get_usable_cache_pool()
            cache_pool_name = cache_pool_name.decode()
        return cache_pool_name

    def _create_cache_pool(self):
        """
        根据需求动态创建一个缓存块，并设置好info，rpwush到list中
        :return:
        """
        num = my_cache.hincrby('CacheInfo', 'instance_number', 1)
        cache_pool_name = 'SQLCachePoolNo.' + str(num)
        my_cache.rpush('SQLCachePoolReadyList', cache_pool_name)

        return cache_pool_name
    def _make_insert_SQL(self):
        """
        制作插入的原生SQL语句
        :return:原生的SQL语句
        """
        params = self.to_dict()
        commit_keys = list()
        commit_values = list()
        for key, value in params.items():
            if value is None:
                continue
            commit_keys.append(key)
            commit_values.append('"{}"'.format(value))

        commit_keys = ', '.join(commit_keys)
        commit_values = ', '.join(commit_values)

        raw_sql = 'INSERT INTO {} ({}) VALUES ({})'.format(self.__tablename__, commit_keys, commit_values)
        return raw_sql


def build_table(model, table_name):
    """
    在数据库中创建表
    :param model: 要创建的表的ORM
    :param table_name: 表的名字，具体创建什么表，由MODEL决定
    :return:无返回值
    """
    table = type(table_name, (model,), {'__tablename__': table_name})
    table.__table__.create(bind=db.engine)


def get_all_table_name():
    """
    获得绑定的数据库的所有表的名字
    :return:字符串列表
    """
    db.reflect()
    return [str(i.name) for i in db.get_tables_for_bind()]


class ModelManager():
    MODEL = None                # 管理的model
    KEYWORD = ''                # model的关键字，一般通过一个大写字母表示，比如device表是D
    UNIQUE_ID = ''              # 每个不同的model的唯一编码，比如device就是mac地址
    # KEYWORD-UNIQUE_ID-创建的日期   每个表的名字的格式，也就是每个model的名字，这三者是关键
    PER_TABLE_MAX_SIZE = 1000000      # 每张表所允许的最大的大小
    """
    工具百宝箱汇总和点评：
    _get_managed_table_name_list：获得这个对象管理的所有表的名字的列表，这是很多操作的第一步
    
    _get_uid_all_time_dict：提供uid，返回字典——键为uid，值为int型的，从小打大排序时间戳列表；这个函数就筛选了符合条件的uid
    _get_uid_query_time_dict：同上，但是这里的时间戳列表是我需要查询的表名的日期部分，所以这个函数通过调用上面一个函数做了
    uid的筛选，自己再做了时间的筛选
    
    _get_model_by_name：获得name对应的model，插入，查询，check都可以用
    _get_models_in_DB：同上，区别在于，_get_models_in_DB保证拿到的model都是有用的（数据库中真实存在的），而且可以查询多个
    name；这个函数的正确用法是，给出一堆你也不知道有没有的table_name，然后给这个函数做筛选
    
    _get_in_using_uid_model_dict：键为uid，值为最新的，也就是还没超过PER_TABLE_MAX_SIZE的表的ORM对象
    
    _make_name：按照规则制作表的名字
    _build_table：在数据库中创建一张表
    """
    @classmethod
    def _get_managed_table_name_list(cls):
        """
        获得所有表的名字，并通过KEYWORD做判断，返回表的名字
        :return:表的名字的字符串列表
        """
        db.reflect()
        return [i for i in get_all_table_name() if cls.KEYWORD == i[0]]

    @classmethod
    def _get_model_by_name(cls, name):
        """
        传入一个表格的名字，返回其对应ORM对象，这一个函数不保证数据库中存在该表
        :param name:表的名字，不可为空
        :return:返回一个ORM对象
        """
        return type(name, (cls.MODEL, ), dict(__tablename__=name))

    @classmethod
    def _get_models_in_DB(cls, names=None):
        """
        传入一些表格的名字，如果存在对应表的表，则返回这些表对应model组成的list（严格保障数据库中有此表）
        :param names:表格的名字的可迭代对象；每个元素应该是string，若为空，则返回所有ORM对象
        :return:ORM对象的list，可能为空list，ORM就是我们自己写的对象，拥有对象内的方法
        """
        db.reflect()
        all_table = dict()
        for table_obj in db.get_tables_for_bind():
            if cls.KEYWORD == table_obj.name[0]:
                all_table[str(table_obj.name)] = table_obj
        if names is None:
            return [type(i, (cls.MODEL, ), dict(__tablename__=i)) for i in all_table.keys()]
        else:
            names = set(names)  # python内部,set使用hash算法，做in判断的时间复杂度为O(1)
            return [type(i, (cls.MODEL, ), dict(__tablename__=i)) for i in all_table.keys() if i in names]

    @classmethod
    def _get_uid_all_time_dict(cls, uids=None):
        """
        查询每个uid的所有表的创建时间，返回对象为dict，键为uid，值为时间戳列表
        :param uids:tuple,set,list都可，其元素为str；若为空，则查所有满足KEYWORD的表
        :return: dict格式，键为mac，值为list，list的值为经过排序的时间
        """
        table_name_list = cls._get_managed_table_name_list()   # 表名列表
        uid_dict = defaultdict(list)   # 键为mac，值为list(int_timestamp)，筛选time
        # 以下一大块，把所有符合目标mac的表都筛选出来，放入mac_dict
        if uids is None:                 # 获得所有的表嘛，就是少做几个判断
            for table_name in table_name_list:
                K, uid, date = table_name.split('-')      # 从名字里面获得各种信息
                uid_dict[uid].append(to_int_timestamp(date, '%Y.%m.%d'))    # 值为时间戳列表
        else:                                   # 如果mac是str，则将它包装进只有一个元素的set中，那个元素就是他自己，
            uids = set(uids)   # 其他时候将其他可迭代对象转为set，这样in操作效率高
            for table_name in table_name_list:
                K, uid, date = table_name.split('-')      # 从名字里面获得各种信息
                if uid in uids:
                    uid_dict[uid].append(to_int_timestamp(date, '%Y.%m.%d'))    # 值为时间戳列表
        # del uids, table_name_list
        for key in uid_dict.keys():
            uid_dict[key].sort()        # 先排个序，方便之后做判断
        return uid_dict

    @classmethod
    def _get_uid_query_time_dict(cls, uids=None, start_time=1546272000, end_time=None):
        """
        query的筛选表这一步的具体实现
        :param uids:tuple,set,list都可，其元素为str；若为空，则查所有uid
        :param start_time:起始时间的时间戳，int和str都可以；若为空，则从19年开始
        :param end_time:格式同上；若为空，则为now
        :return:uid为键，符合查询要求的时间戳为值，需要自己组装成表名
        """
        end_time = int_timestamp() if end_time is None else end_time
        uid_dict = cls._get_uid_all_time_dict(uids)     # 先筛选所有符合mac的表，键为mac，值为时间列表
        # 以下一大块，把所有符合目标时间的表选出来，
        start, end = -1, -1     # 我们需要的范围的下标，最后做timestamp_list[start, end]
        for uid, timestamp_list in uid_dict.items():
            for i in range(len(timestamp_list)-1):      # 先做所在区间的判断，这里一般都能命中，一些特殊情况下面处理
                if timestamp_list[i] <= start_time < timestamp_list[i+1]:
                    start = i
                if timestamp_list[i] <= end_time < timestamp_list[i+1]:
                    end = i + 1
                elif end_time == timestamp_list[i+1]:
                    end = i + 2
            if start == -1:     # 如果小于所有的时间，则为None，切片时效果类似于“空”,否则为0，配合end=0则一个都不选
                start = None if start_time < timestamp_list[0] else 0
            if end == -1:       # None的理由同上,0配合start=0则一个都不选
                end = None if end_time > timestamp_list[-1] else 0
            uid_dict[uid] = timestamp_list[start:end]
        return uid_dict

    @classmethod
    def _get_in_using_uid_model_dict(cls):
        """
        获得最新的表的字典，键为mac，值为model；这个函数的操作较复杂，不适合频繁使用。但是返回的数据最全最真实
        :return:
        """
        uid_time_dict = cls._get_uid_all_time_dict()    # 键为uid，值为时间列表
        result = dict()
        for uid, time_list in uid_time_dict.items():    # 制作最新的表的名字的列表
            table_name = cls._make_name(uid=uid, t=time_list[-1])
            result[uid] = cls._get_model_by_name(table_name)   # 制作最新的表的字典，键为mac，值为model
        # del uid_time_dict, table_name
        return result

    @classmethod
    def _make_name(cls, uid, t=None):
        """
        制作表的name，是制作name的核心原子操作
        :param uid: str类型，表示唯一的编码
        :param t: 时间戳或str日期，默认为当下
        :return: str类型
        """
        t = int_timestamp() if t is None else t
        # 这里就严格遵循了表的名字的格式：KEYWORD-UNIQUE_ID-创建的日期
        if isinstance(t, str):
            return '-'.join([cls.KEYWORD, uid, t])
        else:
            return '-'.join([cls.KEYWORD, uid, to_formatted_time(t, form='%Y.%m.%d')])

    @classmethod
    def _build_table(cls, table_name):
        build_table(cls.MODEL, table_name)

if __name__ == '__main__':
    pass

