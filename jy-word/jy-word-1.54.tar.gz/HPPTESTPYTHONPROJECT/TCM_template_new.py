# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2019/5/28 0028
__author__ = 'huohuo'
from jy_word.File import File
from jy_word.web_tool import format_time
import uuid
my_file = File()


# def get_uuid():
#     uid = uuid.uuid1().hex
#     return uid
#
#
# templates = my_file.read('tcm_template.json')
# # print d
# templates1 = []
# for template in templates:
#     blocks = template.get('items') or []
#     template['template'] = get_uuid()
#     blocks2 = []
#     for block in blocks:
#         bb = block.get('items') or []
#         block['entry_name'] = block['title']
#         del block['title']
#         block['block_id'] = get_uuid()
#         bb1 = []
#         for item in bb:
#             print item.keys(), item.get('text')
#             input_items = item.get('input_items') or []
#             for ii in input_items:
#                 # print ii.keys()
#                 uid = get_uuid()
#                 ii['item_id'] = uid
#                 ii['item_name'] = ii.get('label')
#                 if 'field' in ii:
#                     ii['field'] = ii['item_id']
#                 # elif ii.get('is_group'):
#                 #     group = ii.get('is_group')
#                 #     print ii
#                 elif 'items' in ii:
#                     group = ii.get('is_group')
#                     items = ii.get('items')
#                     for iiii, iii in enumerate(items):
#                         if 'field' in ii:
#                             iii['field'] = get_uuid()
#                         elif group:
#                             iii['field'] = '%s%s' % (uid, iiii)
#                         else:
#                             print iii
#                 elif ii.get('is_list'):
#                     data = ii.get('data')
#                     ids = []
#                     for datai in range(len(data)):
#                         ids.append('%s%s' % (uid, datai))
#                     ii['uuids'] = ids
#                 else:
#                     print ii.keys()
#                 # for k in ii:
#                 #     if (type(ii[k])) not in ['unicode', 'str']:
#                 #         ii[k] = json.dumps(ii[k])
#             bb11 = {'items': input_items, 'entry_name': item.get('text'), 'block_id': get_uuid()}
#             for k in item.keys():
#                 if k not in bb11:
#                     bb11[k] = item[k]
#             bb1.append(bb11)
#         blocks2.append(bb1)
#     templates1.append(blocks2)
#
#
# # my_file.write('tcm_template1.json', templates)
# import requests
# import easygui as eg
# from requests.auth import HTTPBasicAuth
#
# auth = HTTPBasicAuth('hpp_test', 'hpp.123456')
# headers = {'Content-Type': 'application/json'}
# print auth.username
# rq_template = get_uuid()
# template_name = '普适版%s' % format_time(frm='%m%d%H%M')
# template_name = eg.enterbox('模板标题', default=template_name)
#

rq_data = my_file.read('tcm_template_online.json')[0]
template_info = rq_data.get('template_info')
template_info1 = []
for tem in template_info:
    new_tem = [ ]
    for block in tem:

        items = block.get('items')
        items_info = []
        for item in items:
            display_control_item = {}
            for k2 in item.keys():
                if k2 not in ['item_name', 'item_id', 'description']:
                    display_control_item[k2] = item[k2]
            new_item = {
                'item_name': item.get('item_name'),
                'item_id': item.get('item_id'),
                'description': item.get('field'),
                'display_control': display_control_item
            }
            items_info.append(new_item)

        display_control = {}
        for k in block.keys():
            if k not in ['block_id', 'items', 'text', 'input_items', 'entry_name']:
                display_control[k] = block.get(k)
        new_block = {
            'block_name': block.get('entry_name'),
            'block_id': block.get('block_id'),
            'items_info': items_info,
            'description': block.get('text') or '',
            'display_control': display_control
        }
        new_tem.append(new_block)
    template_info1.append(new_tem)

my_file.write('template_online_new.json', template_info1)

if __name__ == "__main__":
    pass
    

