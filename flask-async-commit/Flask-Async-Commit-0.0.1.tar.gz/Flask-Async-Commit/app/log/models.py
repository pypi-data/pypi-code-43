# coding: utf-8
from collections import defaultdict
from common.model_helper import DictAble, QuickSave, CacheSave, ModelManager, build_table
from common.time_helper import to_formatted_time, to_int_timestamp, int_timestamp, formatted_time_list
from configs.db_config import db, my_cache
from configs.application import app


class Device(db.Model, QuickSave, CacheSave):
    """
    并不能直接使用的一个类，必须通过DeviceManager来创建实例
    """
    # 超级重要的一个参数，失去了她，在工厂中就不能覆盖tablename
    __abstract__ = True
    __tablename__ = 'device'
    __table_args__ = {
        'mysql_charset': 'utf8',
        'mysql_engine': 'MyISAM',
        'extend_existing': True
    }
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_time = db.Column(db.Integer, nullable=False, index=True)
    customer_mac = db.Column(db.BigInteger, nullable=False)
    rssi = db.Column(db.SmallInteger, nullable=False)


class DeviceManager(ModelManager):
    MODEL = Device                # 管理的model
    KEYWORD = 'D'                # model的关键字，一般通过一个大写字母表示，比如device表是D
    UNIQUE_ID = 'mac'              # 每个不同的model的唯一编码，比如device就是mac地址，下面会简称uid
    # KEYWORD-UNIQUE_ID-创建的日期   每个表的名字的格式，也就是每个model的名字，这三者是关键
    PER_TABLE_MAX_SIZE = 1000000      # 每张表所允许的最大的大小

    @classmethod
    def query(cls, macs=None, start_time=1546272000, end_time=None, options=None):
        """
        查询数据
        :param mac:tuple,set,list都可，其元素为str；若为空，则表明查所有mac
        :param start_time:起始时间的时间戳，int和str都可以；若为空，则从19年开始
        :param end_time:格式同上；若为空，则为now
        :param options: 可选参数为rssi, customer, raw，分别返回不同的格式的数据
        :return:
        """
        end_time = int_timestamp() if end_time is None else end_time
        # 具体实现流程:筛选出所有的符合条件的表的名字 -> 获得这些表的ORM -> 对这些表做查询 -> 自己整理结果
        # 具体代码流程:_get_uid_query_time_dict() -> _get_model_by_name -> model.query-> No one does me better than me
        mac_dict = cls._get_uid_query_time_dict(uids=macs, start_time=start_time, end_time=end_time)   # 天才第一步
        result = defaultdict(list)
        # 将字典重新组装成str， 这里每一个表都将连续地经历后面三步
        for mac, timestamp_list in mac_dict.items():   # 对每一个mac                         
            for t in timestamp_list:                    # 对mac下的每一个表（不同时间）
                table_name = cls._make_name(mac, t)     # 组装成name
                m = cls._get_model_by_name(table_name)        # 天才第二步（获得ORM）
                if options == 'rssi':
                    data = m.query.with_entities(m.date_time, m.rssi). \
                        filter(m.date_time.between(start_time, end_time)).all()     # 天才第三步
                    result[mac].extend([dict(datetime=i[0], rssi=i[1]) for i in data])      # 天才第四步
                elif options == 'customer':
                    data = m.query.with_entities(m.date_time, m.customer_mac). \
                        filter(m.date_time.between(start_time, end_time)).all()
                    result[mac].extend([dict(datetime=i[0], rcustomer_mac=i[1]) for i in data])
                elif options == 'raw':
                    data = m.query.with_entities(m.date_time, m.customer_mac, m.rssi). \
                        filter(m.date_time.between(start_time, end_time)).all()
                    result[mac].extend([dict(datetime=i[0], customer_mac=i[1], rssi=i[2]) for i in data])
        return result

    @classmethod
    def insert(cls, device_mac, customer_mac, rssi, date_time):
        """
        用起来非常简单的函数，给值，然后我插入就完事了，无返回值
        :param device_mac:设备的mac地址
        :param customer_mac:消费者的mac地址
        :param rssi:距离
        :param date_time:时间
        :return:无
        """
        if my_cache.exists(device_mac):
            table_name = str(my_cache.get(device_mac))      # 从redis缓存中获得表名
            m = cls._get_model_by_name(table_name)      # 这是一个类
        else:
            mac_model_dict = cls._get_in_using_uid_model_dict()
            m = mac_model_dict[device_mac]              # 这是一个类
            my_cache.set(device_mac, m.__name__)        # 键为mac地址，值为表名，做缓存
            my_cache.expire(device_mac, 8*3600)         # 八小时过期
            # del mac_model_dict
        m = m(date_time=date_time, customer_mac=customer_mac, rssi=rssi)    # 这是一个对象
        # m.quick_save()
        m.cache_save()
        # del m

    @classmethod
    def daily_check_build(cls):
        """
        每天检查所有的表，如果超出PER_TABLE_MAX_SIZE就创建新表
        """
        db.app = app
        with db.app.app_context():
            print(r"Hi! I'm check each table!")
            # 代码逻辑：获得所有的mac地址和其所有表的时间，取出最新的表；判断其长度，决定是否创建一个新表
            # 第一步：获得所有最新的表的model
            mac_dict = cls._get_in_using_uid_model_dict()
            # 第二步：检查长度，创建新表
            for m in mac_dict.values():
                count = db.session.query(db.func.count('*')).select_from(m).scalar()
                if count >= cls.PER_TABLE_MAX_SIZE:
                    mac = str(m.__name__).split('-')[1]         # 拿出mac地址
                    new_table_name = cls._make_name(uid=mac)
                    build_table(cls.MODEL, new_table_name)
                    my_cache.set(mac, new_table_name)           # 键为mac地址，值为表名，更新缓存


if __name__ == '__main__':
    print(DeviceManager.query(macs=['00016C06A629']))
