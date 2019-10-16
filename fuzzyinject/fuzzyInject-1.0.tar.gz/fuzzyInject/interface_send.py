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
# import sys
# reload(sys)
# sys.setdefaultencoding('UTF-8')
import yaml
import requests




#组装get的请求方法
def send_get_method(url,params,cookies):
    req ={}
    params_str = ''
    if params != '{}':
    	for params_key,params_value in params.items():
    		params_str = params_str + params_key + '=' + str(params[params_key]) + '&'
    		params_str = params_str[:-1]
    		# print params_str
    		url = url + '?' +params_str 
    req = requests.get(url,cookies=cookies)
    print ("请求结果")
    print (req)
    req = req.json()
    req = json.dumps(req,sort_keys=True, indent=2, separators=(',', ': '), ensure_ascii=False)
    return req


# 组装post的请求方法
def send_post_method(url,params,cookies):
	headers = {}
	# headers = {'Content-Type':'application/json;charset=UTF-8'}
	req = {}
	params = json.dumps(params)
	params = params.replace('\"[','["')
	params = params.replace(']\"','"]')
	params = params.replace('\"false\"','false')
	params = params.replace('\"true\"','true')
	params = json.loads(params)
	req = requests.post(url,data=params,headers=headers,cookies=cookies)
	print ("请求结果")
	print (req)
	req = req.json()
	req = json.dumps(req,sort_keys=True, indent=2, separators=(',', ': '), ensure_ascii=False)
	return req


		

#接口请求逻辑相关代码
def assemble_request(request_method,request_url,params_get,cookies):
	if request_method == 'GET':
		if params_get != {}:
			req_get = send_get_method(request_url,params_get,cookies)
			return req_get
		else:
			req_get = send_get_method(request_url,'{}',cookies)
			return req_get
	if request_method == 'POST':
		if params_get != {}:
			req_post = send_post_method(request_url,params_get,cookies)
			return req_post
		else:
			req_post = send_post_method(request_url,'{}',cookies)
			return req_post


#组装请求参数和fuzzy的分配逻辑相关代码
def assemble_params(request_method,request_url,request_query,request_formdata,params_yaml,phone_cookie_yaml):
	request_result_list = []
	params_get = {}
	params_get_list = []
	params_test = read_yaml(params_yaml)
	cookies = get_cookie(phone_cookie_yaml)
	request_result_url = []
	if len(request_query) >0:
		result = assemble_request(request_method,request_url,'{}',cookies)
		params_get_list.append(str('{}'))
		request_result_list.append(result)
		request_result_url.append(request_url + "\n\t请求方法:" + request_method )
		for params_index in range(0,len(params_test)):
			params_get.clear()
			for query_index in range(0,len(request_query)):
				params_get[request_query[query_index]] =params_test[params_index]
				result = assemble_request(request_method,request_url,params_get,cookies)
				params_get_list.append(str(params_get))
				request_result_list.append(result)
				request_result_url.append(request_url + str(params_get) + "\n请求方法:" + request_method)
				result = ''
	elif len(request_formdata) > 0:
		result = assemble_request(request_method,request_url,'{}',cookies)
		params_get_list.append(str('{}'))
		request_result_list.append(result)
		request_result_url.append(request_url + "\n\t请求方法:" + request_method )
		for params_index in range(0,len(params_test)):
			params_get.clear()
			for query_index in range(0,len(request_formdata)):
				params_get[request_formdata[query_index]] =params_test[params_index]
				result = assemble_request(request_method,request_url,params_get,cookies)
				params_get_list.append(str(params_get))
				request_result_list.append(result)
				request_result_url.append(request_url + str(params_get) + "\n请求方法:" + request_method)
				result = ''
	else:
		result = assemble_request(request_method,request_url,params_get,cookies)
		params_get_list.append(str(params_get))
		request_result_list.append(result)
		request_result_url.append(request_url + "\n\t请求方法:" + request_method )
		result = ''

	return request_result_list,params_get_list,request_result_url
		



#读取yaml接口字段
def read_yaml(yamlFile):
    f = open(yamlFile)
    f = yaml.safe_load(f)
    return f

#cookie 的公共方法
def get_cookie(phone_cookie_yaml):
	cookies = read_yaml(phone_cookie_yaml)
	return cookies

if __name__ == "__main__":
	# json_file = sys.argv[1]
	f = read_yaml("params.yaml")
	print (f)
	# assemble_request(json_file)
	# send_post_method('','{}')
	



