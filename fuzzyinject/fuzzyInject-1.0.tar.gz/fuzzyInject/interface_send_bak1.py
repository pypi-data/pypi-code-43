#!/usr/local/bin/python
#-*- coding: UTF-8 -*-
#author:lol
#date:2018-05-24

'''
本工程主要用于接口请求、cookie解析等
'''
import jsonpath_rw_ext as jp
import codecs
import json
import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
import parseJson
import yaml
import requests



def get_cookie():

	cookies = {'login_sess':'GOAo2o_FetSCmU2mSowNiioT8afLOxauQgZzU98ixVRUEVQyOLYONs17gx9kJEEq6xiZ','phone':'13716054767'}

	return cookies

# get 请求方法
def send_get_method(url,parmas):
    req ={}
    cookies = get_cookie()
    req = requests.get(url,parmas,cookies=cookies)
    print req
    req = parseJson._decode_dict(req.json())
    req = json.dumps(req,sort_keys=True, indent=2, separators=(',', ': '), encoding="UTF-8", ensure_ascii=False)
    return req

# post 请求方法

def send_post_method(url,params):
	headers = {}
	headers = {'Content-Type':'application/json;charset=UTF-8'}
	req = {}
	cookies = get_cookie()
	params = json.dumps(params)
	params = params.replace('\"[','["')
	params = params.replace(']\"','"]')
	params = params.replace('\"false\"','false')
	params = params.replace('\"true\"','true')
	req = requests.post(url,data=params,headers=headers,cookies=cookies)
	print req
	req = parseJson._decode_dict(req.json())
	req = json.dumps(req,sort_keys=True, indent=2, separators=(',', ': '), encoding="UTF-8", ensure_ascii=False)
	return req

#组装逻辑相关代码
def assemble_request(request_method,request_url,request_query):
	params_test = read_yaml('params.yaml')
	params_list = []
	final_result_list = []
	# print request_url
	if request_method == 'GET':
		params_get = {}
		if len(request_query)>0:
		   for query_index in range(0,len(request_query)):
		   	for params_index in range(0,len(params_test)):
					params_get[request_query[query_index]] =params_test[params_index]
					print params_get
					req_get = send_get_method(request_url,params_get)
					print req_get
					params_list.append(params_get)
					final_result_list.append(req_get)
					req_get = ''
					params_get.clear()
		else:
			req_get = send_get_method(request_url,'{}')
			params_list.append(params_get)
			final_result_list.append(req_get)
			req_get = ''


	if request_method == 'POST':
		print request_url
		params_get = {}
		print len(request_query)
		if len(request_query)>0:
			for query_index in range(0,len(request_query)):
				for params_index in range(0,len(params_test)):
					params_get[request_query[query_index]] =params_test[params_index]
					req_post = send_post_method(request_url,params_get)
					params_list.append(params_get)
					final_result_list.append(req_post)
					req_post = ''
					params_get.clear()

		else:
			req_post = send_post_method(request_url,'{}')
        	params_list.append(params_get)
        	final_result_list.append(req_post)
        	req_post = ''

	return params_list,final_result_list





#读取yaml接口字段
def read_yaml(yamlFile):
    f = open(yamlFile)
    f = yaml.load(f)
    fuzzy_params = f['NUMBER_ERRO'] 
    print fuzzy_params
    return fuzzy_params



if __name__ == "__main__":
	# json_file = sys.argv[1]
	f = read_yaml("params.yaml")
        fuzzy_params = f['NUMBER_ERRO']
        print type(fuzzy_params)
	# assemble_request(json_file)
	# send_post_method('http://microloan-operating-activity.yxapp.xyz/wallet/internal/depositRecord/updateAll','{}')
	



