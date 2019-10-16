import bdp
import requests
import json

# data = bdp.read_data("sdfsf")
# print(data)

# url = 'http://localhost:9016'
# print(requests.put(url, timeout=15))
"""
url = 'http://localhost:49499/tb/info'
user_id = '91cfae6d791069bff1ad87ba3962163c'
tb_id = 'tb_13b9ad1cd77f4f30bff84f09104f5024'
fields_id = json.dumps(['fk438cd1ea', 'fk310b0030'])
print(fields_id)
# query_info = {'user_id': user_id, 'tb_id': tb_id, 'fields': fields_id}
query_info = {'user_id': user_id, 'tb_id': tb_id}
origin_data = requests.post(url, data=query_info, timeout=15)
origin_data = origin_data.json().get('result').get('fields')
origin_data = [field.get('field_id') for field in origin_data]
print(origin_data)

url = 'http://localhost:49499/tb/query'
user_id = '91cfae6d791069bff1ad87ba3962163c'
tb_id = 'tb_13b9ad1cd77f4f30bff84f09104f5024'
fields_id = json.dumps(origin_data)
query_info = {'user_id': user_id, 'tb_id': tb_id, 'fields': fields_id, 'limit': 5}
origin_data = requests.post(url, data=query_info, timeout=15)
print(origin_data.json())
# print(bdp.table_list())
"""
print(bdp.table_list())
# print(bdp.table_list())
# print(bdp.read_data('tb_13b9ad1cd77f4f30bff84f09104f5024'))