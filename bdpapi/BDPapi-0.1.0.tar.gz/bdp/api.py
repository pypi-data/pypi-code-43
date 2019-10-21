import numpy as np
import os
import requests
import json


def table_list():

    url = 'tb/list'
    user_id = os.getenv('USERID')
    user_id = '91cfae6d791069bff1ad87ba3962163c'
    query_info = {'user_id': user_id}

    origin_data = post_request(url, query_info)

    data = [{'tb_title': tb.get('title'), 'data_count': tb.get('data_count'), 'tb_id': tb.get('tb_id')}
            for tb in origin_data.get('result')]

    return data


def read_data(tb_id, limit=10000):

    url = 'tb/query'
    user_id = os.getenv('USERID')
    user_id = '91cfae6d791069bff1ad87ba3962163c'
    fields_id = read_tb_fields(tb_id)
    fields_id = json.dumps([field.values()[0] for field in fields_id])
    query_info = {'user_id': user_id, 'tb_id': tb_id, 'fields': fields_id, 'limit': limit}

    origin_data = post_request(url, query_info)

    # 0:integer 1:double 2:string 3:datetime
    data_type = {'integer': 'i', 'double': 'f', 'string': 'S40', 'datetime': 'M'}

    data_result_data = origin_data.get('result').get('data')
    data_result_data = [tuple(data) for data in data_result_data]
    data_result_fields = origin_data.get('result').get('schema')

    data_type = [(field.get('title'), data_type.get(field.get('type'))) for field in data_result_fields]
    data_type = np.dtype(data_type)
    data = np.array(data_result_data, dtype=data_type)

    return data


def read_tb_fields(tb_id):

    url = 'tb/info'
    user_id = os.getenv('USERID')
    user_id = '91cfae6d791069bff1ad87ba3962163c'
    query_info = {'user_id': user_id, 'tb_id': tb_id}

    origin_data = post_request(url, query_info)

    origin_data = origin_data.get('result').get('fields')
    data = [{field.get('title'): field.get('field_id')} for field in origin_data]

    return data


def post_request(url, data, timeout=15):

    # port = utils.Config()
    localhost = os.getenv('DOCKER_HOST')
    url = os.path.join("http://" + localhost, url)

    origin_data = ''
    try:
        origin_data = requests.post(url, data=data, timeout=timeout)
    except Exception as e:
        print(e)

    origin_data = origin_data.json()
    if origin_data.get('status') != '0':
        print(origin_data.get('errstr'))
        return

    return origin_data
