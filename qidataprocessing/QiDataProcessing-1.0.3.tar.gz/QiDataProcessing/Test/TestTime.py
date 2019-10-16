import datetime
from calendar import EPOCH
from numpy import long
import time


def datetime2timestamp(date_time, convert_to_utc=False):
    if isinstance(date_time, datetime.datetime):
        if convert_to_utc:  # 是否转化为UTC时间
            date_time = date_time + datetime.timedelta(hours=-8)  # 中国默认时区
        timestamp = time.total_seconds(date_time - EPOCH)
        return long(timestamp)
    return date_time


def ConvertCSharpTicksToLinuxTicks(value):
    csharpTicks1970 = 621355968000000000
    linuxTicks = (value - csharpTicks1970) / 10000000
    timeZone = 28800
    linuxTicks = linuxTicks - timeZone
    return linuxTicks


# 636793920000000000
# 1553754008
# 1543795200

# 621355968000000000
# linuxTicks = convert_c_sharp_ticks_to_linux_ticks(636909351085100108)
# print(linuxTicks)

dt = datetime.datetime.fromtimestamp(0)
print(dt)


# online_dt = datetime.datetime(1970,1,1,0,0,0)
# online_seconds = int(time.mktime(online_dt.timetuple()))
# print(online_seconds)


class Dog:
    n = '这是一个类变量'  # 类变量
    n_list = []
    name = '这是类的name!'

    def __init__(self, name, weapen, role, money=1234):
        self.name = name

    def shot_down(self):
        print('%s:被击中！' % self.name)

    def buy_gun(self, gun_name):
        print('%s:买了一部%s枪' % (self.name, gun_name))

    def bulk(self):
        print('%s ,Wang Wang Wang!' % self.name)


Dog1 = Dog('superman', 'ak47', 'ploice')  # 实例化两个对象
Dog2 = Dog('X-man', 'b211', 'robber')

print("0:"+Dog.n)
Dog1.n = '这个Dog1对象的类变量'
Dog2.n = '这个Dog2对象的类变量'
print("0:"+Dog.n)
print("1:"+Dog1.n)
print("2:"+Dog2.n)

Dog.n = "更改后的类变量！"
print("0:"+Dog.n)
print("1:"+Dog1.n)
print("2:"+Dog2.n)

Dog1.n_list.append('list_1')
Dog2.n_list.append('list_2')
print(Dog1.n_list)
print(Dog2.n_list)
print(Dog.n_list)

Dog2.n_list.append('123')
print(Dog1.n_list)
print(Dog2.n_list)
print(Dog.n_list)
