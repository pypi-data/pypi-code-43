#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time : 2019/7/22 0022 17:44 
# @Author : HL 
# @Site :  
# @File : test.py 
# @Software: PyCharm
import time
import cityList

clst = cityList.cityList()
if '藁城市' in clst:
    codes = clst['藁城市']
    splt = codes.split(',')
    cityCode = splt[0]
    proCode = splt[1]
    print(cityCode)
    print(proCode)

print(str(time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time()))))
