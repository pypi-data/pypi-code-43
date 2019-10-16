#!/usr/local/bin/python
#-*- coding: UTF-8 -*-
#author:lol
#date:2018-05-24

'''
本工程主要用于yaml解析、组装逻辑处理
'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json
import yaml



#读取yaml接口字段
def read_yaml(yamlFile):
    f = open(yamlFile)
    
    return  yaml.load(f)





if __name__ == "__main__":
	f = read_yaml("params.yaml")
	print f