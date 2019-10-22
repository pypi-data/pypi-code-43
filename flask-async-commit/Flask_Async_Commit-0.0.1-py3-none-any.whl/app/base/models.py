# coding: utf-8
from sqlalchemy.dialects.mysql import TINYINT
from common.model_helper import DictAble, QuickSave
from configs.db_config import db
import sys


class ZoneStructMap(db.Model, DictAble, QuickSave):
    """
        创建区域的层次关系，mall，store等都视为zone，
        type表明了具体是什么,而parent_zone组织了结构关系
        在大悦城项目中，type最高为3，0空缺
    """
    __tablename__ = 'zone_struct_map'
    __table_args__ = {
        'mysql_charset': 'utf8',
        'mysql_engine': 'InnoDB'
    }
    zone_id = db.Column(db.SmallInteger, primary_key=True)
    zone_name = db.Column(db.String(50))
    type = db.Column(TINYINT, nullable=False, server_default='0')
    parent_zone = db.Column(db.ForeignKey('zone_struct_map.zone_id'), index=True)
    size_L = db.Column(TINYINT)
    size_W = db.Column(TINYINT)
    parent = db.relationship('ZoneStructMap', remote_side=[zone_id],
                          primaryjoin='ZoneStructMap.parent_zone == ZoneStructMap.zone_id', backref='zone_struct_maps')

    @classmethod
    def hyper_find_children(cls, zone_id):
        """
            具有极强查询功能的函数，可以找到所有的孩子并返回非常标准的格式
            :param zone_id: 父zone的id号
            :return: 返回此zone的所有child的字典的列表，字典的键值对为其属性
        """
        return [i.to_dict() for i in cls.query.filter_by(parent_zone=zone_id).all()]


class DeviceZoneMap(db.Model, DictAble, QuickSave):
    """
        主要是设备的信息，其主要用途为查询设备到zone的映射
    """

    __tablename__ = 'device_zone_map'
    __table_args__ = {
        'mysql_charset': 'utf8',
        'mysql_engine': 'InnoDB'
    }
    device_id = db.Column(db.Integer, primary_key=True)
    device_mac = db.Column(db.BigInteger, index=True)
    device_name = db.Column(db.String(50), server_default=db.text('NULL'))
    zone_id = db.Column(db.ForeignKey('zone_struct_map.zone_id'), nullable=False, index=True)
    position_x = db.Column(TINYINT, nullable=False)
    position_y = db.Column(TINYINT, nullable=False)
    radius = db.Column(TINYINT, nullable=False)
    alive = db.Column(TINYINT,  server_default='1')
    zone = db.relationship('ZoneStructMap', primaryjoin='DeviceZoneMap.zone_id == ZoneStructMap.zone_id',
                        backref='device_zone_maps')

    @classmethod
    def hyper_device_of_zone(cls, zone_id_list=None, alive_list=None):
        """
            具有极强查询功能的函数，可以找到zone下的所有设备，并返回非常标准的格式
            :param alive_list: alive的值组成的列表
            :param zone_id_list: zone_id组成的列表
            :return: 返回此zone的所有child的字典的列表，字典的键值对为其属性
        """
        # select, where这些变量名都对应这sql语句中的一部分，SQLAlchemy做的实际上就是字符串拼接，分开写可以增加可读性
        filter1 = cls.zone_id.in_(zone_id_list) if zone_id_list is not None else db.text('true')
        filter2 = cls.alive.in_(alive_list) if alive_list is not None else db.text('true')
        select = db.session.query(cls.device_mac, cls.device_name, cls.device_id, cls.zone_id,
                                  db.func.format(cls.position_x/100, 2), db.func.format(cls.position_y/100, 2),
                                  db.func.format(cls.radius/10, 1), cls.alive)
        where = select.filter(filter1, filter2)
        db_result = where.all()
        result = [dict(device_mac=i[0], device_name=i[1], device_id=i[2], zone_id=i[3],
                       position_x=float(i[4]), position_y=float(i[5]),
                       radius=float(i[6]), alive=i[7])
                  for i in db_result]
        return result

    @classmethod
    def hyper_device_of_child_zone(cls, zone_id):
        """
            具有极强查询功能的函数，可以找到zone的child_zone
            下的所有设备，并返回非常标准的格式
            :param zone_id: parent_zone的id号
            :return: 返回字典列表，字典为child_zone的属性，额外的属性包括child_list
            其为字典列表，字典为child_child_zone属性，额外的属性包括device_list，其为设备属性的字典的列表
        """
        child_zone_id_list = db.session.query(ZoneStructMap.id).filter_by(parent_zone=zone_id)
        chind_child_zone_id_list = db.session.query(ZoneStructMap.id).filter_by(ZoneStructMap.parent_zone.in_(child_zone_id_list))
        devices = db.session.query(cls).filter_by(cls.zone_id_in(chind_child_zone_id_list))
        # result = []
        # for second_zone in ZoneStructMap.hyper_find_child(zone_id):
        #     second_list = []
        #     for buttom_zone in ZoneStructMap.hyper_find_child(second_zone['zone_id']):
        #         buttom_zone['device_list'] = [i.to_dict() for i in
        #                                           DeviceZoneMap.query.filter_by(zone_id=buttom_zone['zone_id']).all()]
        #         second_list.append(buttom_zone)
        #
        #     second_zone['child_list'] = deepcopy(second_list)
        #     result.append(second_zone)
        # return result


if __name__ == '__main__':
    from configs.db_config import session_factory
    session = session_factory()
    # zone_id = 1
    # zone_id_list = [9, '10']
    # alive_list = None
    # filter1 = DeviceZoneMap.zone_id.in_(zone_id_list) if zone_id_list is not None else text('true')
    # filter2 = DeviceZoneMap.alive.in_(alive_list) if alive_list is not None else text('true')
    # select = session.query(DeviceZoneMap.device_mac, DeviceZoneMap.device_name, DeviceZoneMap.device_id, DeviceZoneMap.zone_id,
    #                           func.format(DeviceZoneMap.position_x / 100, 2), func.format(DeviceZoneMap.position_y / 100, 2),
    #                           func.format(DeviceZoneMap.radius / 10, 1), DeviceZoneMap.alive)
    # # where = select.filter(filter1, filter2) if filter1 is not None and filter2 is not None else select
    # where = select.filter(filter1, filter2)
    # print filter1
    # print filter2
    # print where
    # print where.all()

    # m1 = DeviceZoneMapinsert(device_mac=8888888, zone_id=1,
    #                           position_y=50, position_x=50, radius=60)
    m2 = DeviceZoneMap(device_mac=8888888, zone_id=1,
                       position_y=50, position_x=50, radius=60)

    d = m2.__dict__
    del d['_sa_instance_state']
    m3 = DeviceZoneMap(**d)
    print(m3.__dict__)
    print('m2', m2.__sizeof__())
    print('m2', sys.getsizeof(m2))
    print('d', d.__sizeof__())
    print('d', sys.getsizeof(d))
    print('m3', m3.__sizeof__())
    print('m3', sys.getsizeof(m3))


