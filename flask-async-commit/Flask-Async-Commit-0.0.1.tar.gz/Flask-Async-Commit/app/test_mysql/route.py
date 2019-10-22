# ! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint
import time
from common.model_helper import ModelManager, build_table
from common.time_helper import int_timestamp
from app.log.models import DeviceManager, Device
import random
from common.APSmission import async_retry
from app.test_mysql.models import PriMac
from configs.application import app
from configs.db_config import my_cache
from redis import ConnectionError
import gevent
import os

test_mysql = Blueprint('test_mysql', __name__)


connection_error = 0
# 'abc' = 'sadfghjklm'*100


# @asyn_repeat(app=app)
# def test_aps():
#     global connection_error
#     # print 'test aps'
#     try:
#         m = SimpleTable(xixi=123)
#         m.quick_save()
#         # m.cache_save()
#     except ConnectionError:
#         connection_error += 1

# @asyn_repeat(app=app)


@test_mysql.route('/')
def test():
    g = gevent.spawn(test_aps)
    g.start()
    # test_aps()
    return 'success'

def test_aps():
    m = PriMac(str1='abc', str2='abc', str3='abc', str4='abc', str5='abc', str6='abc',
               str7='abc', str8='abc', str9='abc', str10='abc', str11='abc', str12='abc')
    m.cache_save()
    # m.quick_save()

@async_retry(app=app)

@test_mysql.route('/info')
def get_list():
    line = [i.decode() for i in my_cache.lrange('SQLCachePoolReadyList', 0, -1)]
    print('list:', line)
    print('dict:', my_cache.hgetall('CacheInfo'))
    return 'success'

@test_mysql.route('/clear')
def clear_():
    print(my_cache.delete('SQLCachePoolReadyList'))
    print(my_cache.delete('CacheInfo'))
    return 'success'

@test_mysql.route('/count')
def count_sql():
    print('***', 'count(SQL-list)', my_cache.llen('SQL-list'), '***')
    return 'success'

def test_verify():
    return True

def len_set():
    print('***', 'count(set)', my_cache.scard('aps test'), '***')
# def test_aps():
#     # print 'my pid', os.getpid()
#     my_cache.sadd('aps test', str(time.time()) + str(random.random()))
#     a = 2/0

# @test_mysql.route('/count')
# def count_set():
#     print '***', 'count(set)', my_cache.scard('aps test'), '***'
#     return 'success'
#
# @test_mysql.route('/clear')
# def clear_set():
#     my_cache.delete('aps test')
#     return 'success'

@test_mysql.route('/req_cnt')
def req_cnt():
    print('mypid', os.getpid(), 'request count', app.cnt, 'error count', connection_error)
    return 'success'






# def make_tables():
#     start = 140737488355328
#     end = 281474976710655
#     mac_list = []
#     for i in range(200):
#         mac = hex(random.randint(start, end)).replace('0x', '').upper()
#         print mac
#         mac_list.append(mac)
#         table_name = DeviceManager._make_name(mac)
#         DeviceManager._build_table(table_name)
#     print mac_list


def auto_check_build():
    DeviceManager.daily_check_build()


def insert():
    # macs = ['00016D06A629', '00016C06B130', '00016C0E2931']
    # r = randint(0, 2)
    macs = ['BC3F93B912ED', 'C0C71C80B56E', 'BD8C823D2E20', 'A5D98408B665', '84A4ADC7F5AC', '9DB7DC3C0606', 'DA0A64610D8F',
     'B37B0024B4DE', 'B1AEE0A3CCFF', 'F77DB81BD1CD', '8484025B49FB', 'A0210BA5028B', 'C1FE81C20B3B', 'C22151A50EA9',
     'E9034283E54C', 'FC7B4178E0AF', '9FB6C3D592DB', 'E1CE80D1E616', '8BDF19D9715E', 'FC040352DCD7', 'E97C8DABD9D5',
     '8A713BC356A8', 'E190FA1F29B7', 'EDB5B2A2E818', 'DF517026F740', '8043B2A2A707', 'BC3EF0A12D01', 'E7EDDB87A710',
     'ADFEC5FA8517', 'B8762DDBE4B2', 'F77F3ADE27BE', 'F1E9E691C175', 'AFAA88838855', 'E4503998DAEF', 'FA985BA117AB',
     '921C62448B91', 'C3179F7B2454', 'A321E1E620AA', '9B9B740C33D1', '9AF3FEC081AA', '99BAF751DEA6', 'F1380C5C2777',
     'E68B16B08CD7', 'C7D45C830028', 'C38563EC1A02', 'D7E4024F2223', 'F63A1C8496F9', '9E3B85A193F8', 'B49DC3F832F2',
     'C93F52A92463', 'E284B9F4AF34', 'AAC5BB6F3391', '908B778EF268', 'FEE9EED1F12D', '8B71B1028697', 'FCE9C3FF31D9',
     'A33CD4928D91', '8F90AA363E89', '8F3D2038BA8B', 'EF6944BA8220', '81103287A16B', 'B72E101BE4A3', 'B773956D52E3',
     'E73EA4429F43', 'FCA55DAD094E', 'AFE784BE07DE', 'F9CCEB2E4D7C', 'FCA6DAD7AEB9', 'D4D33A0A408A', 'C8E69E34C6E7',
     '8A9A2DEDDB18', 'D2F0C1E02A28', 'CB305425FC99', 'E1AF302726FF', '8C59FA607D33', 'E86DF636FE09', 'BA0BA79CB116',
     'DB5D19D61D6B', 'C07BA4A0F3C2', '89726D8157FE', 'E01E0C97402B', 'E9305E587F50', 'B9611740B05E', 'C41402C2AD88',
     'A10360F539B4', 'FB0218D2ED93', '9D3A00D5843F', 'BA95637D6379', 'FB59D3A97DEE', '93F57227824D', 'E6DA26E809E1',
     '9E360744C125', 'E0897360F77F', 'CF3F6F57F876', '829A6A16FD0C', 'AC77B8318B7A', '9485E79A5B56', 'E19E5BAA2F98',
     '8E8B09C3A262', '8C4322E54A30', 'F0B97E7C9FCD', '99B5A24B4D13', 'CEC4E4C9DEA9', 'BEB1DF3221FC', 'A605782DC234',
     '9F39C973F5D1', 'C88132A095F7', '885B7DC1661A', '9A1C546B0BC2', 'A2068C40E636', 'C80264DE9F48', 'C8898A7C8C8C',
     '9B2DC4CBA9D9', 'BD29BE186330', 'E3123E6712D1', 'B2C4B7D50669', 'DD8C478375FD', '98CEDB753900', 'EAE741A1F53D',
     '9A8115D7F411', '9790B4DDA089', 'D9498E317727', 'D720B9DEEEFD', 'FA5E12DE892F', '94B7997BAB96', 'C46C3DE8783C',
     'E099B48F9E08', 'EEE4736D3B39', '8A9D0C655130', 'DDD6C5B58166', 'F78FEB24FBEA', 'BFAA30887812', 'EE9784A73C48',
     'C04BEC2B6589', 'FF1EFE314F63', 'D76D38CE51E0', 'C84A85E28783', 'DC1725E03962', 'DA3905600A6B', 'E035CA747751',
     'C68318316027', 'D76ECA3D5C49', 'AAD590629F7F', 'C1192BC5414E', 'E78D518DEC46', 'FF48C4B25E5A', '826FAE29ABCC',
     'FC88310130BE', 'A353107D57CA', 'ED59830EC3AB', 'B1A3081B8CBD', '99503A8C99E4', 'F47B0EFFBD6F', 'F771496BAACF',
     '8B6AF4FF2FFE', 'AF21D2B29484', 'A756E680D3E4', 'D16D87F99794', 'F8DFF380EF6C', 'CB9125B446F5', 'C7A7BCCDA823',
     'BA0DED8E0EEE', 'AC215C8E9647', 'E838E6CFC1A7', 'BAAA6B14EA75', 'B878AD8C8F43', 'F3FDE5A831CA', '98CFE5C062DC',
     'CA179C8FC70B', 'A9F5ECB666AC', '8163AC520754', 'C1127E4328EE', 'B8714D3437D6', 'ADBB5F94B8A5', 'C5CBF8202F6A',
     'B3BFD7865792', 'B0172CC5AD6D', 'BDCD5B9FD7BD', 'B18A8FF831A7', 'BF3849709501', 'F48B9D588508', '965C8E617749',
     'A21A26CEB647', 'F4F46E4EB132', 'F9DC7C8F4ED5', 'A5748658B924', 'DDE7389F3757', 'F316FA7DD9BA', 'CB5E926DDEF6',
     'C3009D99A63F', '90A3DCB0A435', '84BA08DFD0A9', 'C3254482804C', 'CCCAF77916A7', 'D157D055D6D7', 'C8E20536F34F',
     'D9D84BD98FD5', 'C36FA709711F', 'CFB6766C36BA', 'DF0DF35C096E']
    r = random.randint(0, 199)
    # print '*' * 30
    # print ''
    # print '*' * 30
    DeviceManager.insert(device_mac=macs[r], customer_mac=23333, rssi=6, date_time=int_timestamp())


# def make_query_test():
#     print '*' * 30
#     result = DeviceManager.query(mac='00016C06A629', end_time=1564970424, options='rssi')
#     print result
#     print '*' * 30


def make_some_table():
    macs = ['00016D06A629', '00016C06B130', '00016C0E2931']
    times = [1561957761, 1562735361, 1561439361]
    line = []
    for mac in macs:
        for t in times:
            build_table(Device, DeviceManager.make_name(mac, t))


def make_model(model, mac):
    return model(mac=mac, str1=mac, str2=mac, str3=mac, str4=mac, str5=mac,
                 str6=mac, str7=mac, str8=mac, str9=mac, str10=mac, str11=mac)

def make_model_1(model, mac):
    return model(mac=mac, str1=str(mac)*1000)

# def append_mac(model):
#     # print(1)
#     pri = 0
#     f = open('app/test_mysql/mac.txt', 'r')
#     start = time.time()
#     while pri < 10000:
#         for i in range(50):
#             try:
#                 rad = int(f.readline().strip())
#             except:
#                 break
#             a = make_model_1(model, rad)
#             a.cache_save()
#             # a.quick_save()
#             pri += 1
#         print pri
#     end = time.time()
#     s = '%d notes: %f' % (pri, end - start)
#     print s
#     f.close()
    return