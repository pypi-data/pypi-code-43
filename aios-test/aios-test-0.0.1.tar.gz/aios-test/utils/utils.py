# -*- coding: utf-8 -*-
import os
import sys
import time
import base64
import string
import logging
import requests
import traceback
import importlib
import threading
import itertools
from random import choice

TIMEOUT = 600
JPG_FORMATS = ['.JPG', '.JPEG', '.jpg', '.jpeg']
PNG_FORMATS = ['.PNG']
PIPELINE_TOKEN_FOREVER = 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1Njg2MjcyMDgsIm5iZiI6MTU2ODYyNzIwOCwianRpIjoiZjc3YmM1N2QtYWNlNS00MjllLTk5Y2EtMzc5ZmZjNmI1ODQzIiwiaWRlbnRpdHkiOnsiY3VycmVudF91c2VyIjp7ImlkIjotMSwidGVuYW50X2lkIjoxLCJjcmVhdGVkX2F0IjpudWxsLCJjcmVhdGVkX2J5IjpudWxsLCJ1cGRhdGVkX2F0IjoiV2VkLCAzMSBKdWwgMjAxOSAwNjowMzozOSBHTVQiLCJ1cGRhdGVkX2J5Ijo1MywibmFtZSI6InBpcGVsaW5lQGludGVsbGlmLmNvbSIsIm5pY2tuYW1lIjoicGlwZWxpbmUiLCJmdWxsbmFtZSI6InBpcGVsaW5lIiwidGVsIjpudWxsLCJlbWFpbCI6InBpcGVsaW5lQGludGVsbGlmLmNvbSIsImFkZHJlc3MiOiIiLCJnZW5kZXIiOjAsInR5cGUiOiJlbWFpbCIsInJlbWFyayI6bnVsbCwiYXZhdGFyIjpudWxsLCJzdGF0dXMiOnRydWUsImlzX3VwZGF0ZV9uYW1lIjpmYWxzZSwiaXNfdmVyaWZ5Ijp0cnVlLCJpc19jb25maXJtIjp0cnVlLCJpc190ZW5hbnRfbWFpbiI6ZmFsc2UsInByb3RvY29sX3ZlcnNpb24iOjEsInJvbGVzIjpbXSwidGVuYW50X25hbWUiOiJcdTZkZjFcdTU3MzNcdTRlOTFcdTU5MjlcdTUyYjFcdTk4ZGVcdTYyODBcdTY3MmZcdTY3MDlcdTk2NTBcdTUxNmNcdTUzZjgifX0sImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyIsInVzZXJfY2xhaW1zIjp7ImN1cnJlbnRfcm9sZXMiOlsiZGVmYXVsdCJdfX0.Hs-19WRuDRIUaXzleg85S_REGC8kjXx1gSYpGsKA2zI'

def assert_true(condition, msg):
    if condition:
        print('{}   √'.format(msg))
    else:
        print('{}   ×'.format(msg))
    return condition

def set_up_log():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s  %(message)s',
                                  '%Y-%m-%d %H:%M:%S')
    console = logging.StreamHandler(stream=sys.stdout)
    console.setFormatter(formatter)
    console.setLevel(logging.DEBUG)
    logger.addHandler(console)

def generate_secret_key(length=8):
    """Generate secret key"""
    return "".join([choice(string.hexdigits).lower() for i in range(length)])

def get_uniq_id():
    return '%s%s' % (time.strftime('%Y%m%d%H%M%S'), generate_secret_key(8))

def b64encode(text):
    if not isinstance(text, bytes):
        text = str(text).encode('utf-8')
    return base64.b64encode(text).decode('utf-8')

def b64decode(secret):
    return base64.b64decode(secret).decode('utf-8')

def cartesian_join(lbs):
    # 获取多标签的笛卡儿积组合
    # input: [{"交通工具": ["摩托", "飞机"]}, {"材质": ["铁", "合金"]}]
    # output 交通工具.材质, ["摩托.铁", "飞机.铁", "摩托.合金", "飞机.合金"], [[0, 0], [1, 0], [0, 1], [1, 1]]
    lb_keys = []
    lb_values = []
    _lbs = lbs.copy()
    while len(_lbs):
        lb = _lbs.pop(0)
        while not isinstance(lb, list):
            lb_keys.append(list(lb)[0])
            lb = lb.get(list(lb)[0])
        else:
            lb_values.append(lb)

    def cov_index(its, lb_values):
        indexes = []
        for index, it in enumerate(its):
            indexes.append(lb_values[index].index(it))
        return indexes

    label_comps = ['.'.join(item) for item in itertools.product(*lb_values)]
    label_indexes = [cov_index(item, lb_values) for item in itertools.product(*lb_values)]
    return lb_keys, label_comps, label_indexes
    
def convert_labels_multi_2_single(labels):
    # output: [{"交通工具.材质": ["摩托.铁", "飞机.铁", "摩托.合金", "飞机.合金"]}]
    if len(labels.get('label')) > 1:
        main_label = {}
        main_keys = []
        main_values = []
        for label in labels.get('label'):
            main_keys.append(list(label)[0])
        comps_keys, comps, indexes = cartesian_join(labels.get('label'))
        main_label.setdefault('.'.join(comps_keys), comps)
        labels['label'] = main_label

        # 转换数据
        for data in labels.get('data'):
            idx = _.index_of(indexes, data.get('label'))
            data['label'] = [idx]

    return labels

def get_img_fmt_quality(img_path):
    _, img_fmt = os.path.splitext(img_path)
    if img_fmt.upper() in JPG_FORMATS:
        quality = 95
    elif img_fmt.upper() in PNG_FORMATS:
        quality = 9
    else:
        logging.error('this image format not correct %s' % img_path)
        return False, ''
    return quality, img_fmt
    
def get_label(label_type, one_picture, img_width=32, img_height=32):
    if label_type == 'box':
        # 格式参考 https://gluon-cv.mxnet.io/build/examples_datasets/detection_custom.html
        label = [4, 5, img_width, img_height]
        for item in one_picture['boxes']:
            item['box'][0] /= float(img_width)
            item['box'][2] /= float(img_width)
            item['box'][1] /= float(img_height)
            item['box'][3] /= float(img_height)
            one_label = [int(item['class'])] + item['box'] + item.get('label', [])
            label += one_label
        
    elif label_type == 'classification':
        lb = one_picture['label']
        label = lb[0] if isinstance(lb, list) else lb
    elif label_type == 'segmentation':
        label = None
    else:
        label = one_picture['label']

    return label

def try_to_request_async(uri, params, try_num=3, interval=5):
    flag, data = False, None
    headers = {'Authorization': PIPELINE_TOKEN_FOREVER}
    while try_num > 0:
        try:
            export_res = requests.post(uri, json=params, timeout=TIMEOUT, headers=headers)
            export_res = export_res.json()
            if export_res.get('status'):
                export_id = export_res.get('data').get('export_id')
                # 定时查询状态
                start_time = time.time()
                json_path = None
                while time.time() - start_time < 10 * 60:
                    time.sleep(interval)
                    logging.info('{}: try to check export status, export_id {}...'.format(time.time(), export_id))
                    status_res = requests.get(uri, params={'export_id': export_id}, timeout=TIMEOUT, headers=headers)
                    status_res = status_res.json()
                    if status_res.get('status'):
                        json_path = status_res.get('data').get('path')
                        if json_path:
                            flag, data = True, json_path
                            break
                if flag:
                    break
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            try_num -= 1

        time.sleep(10)

    if flag is False:
        sys.exit(1)
    logging.info('response: {}'.format(data))
    return data, export_res.get('data')

def try_to_request(uri, params, try_num=3):
    flag, data = False, None
    headers = {'Authorization': PIPELINE_TOKEN_FOREVER}
    while try_num > 0:
        try:
            res = requests.post(uri, json=params, timeout=TIMEOUT, headers=headers)
            res = res.json()
            if res.get('status'):
                logging.info('deploy to %s succeed' % uri)
                flag, data = True, res.get('data')
                break
            else:
                msg = res['message']
                logging.info('deploy to %s failed, the reason is %s' % (uri, msg))
                try_num -= 1
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            try_num -= 1

        time.sleep(10)

    if flag is False:
        sys.exit(1)
    logging.info('response: {}'.format(data))
    return data

def try_to_get_request(uri, params, try_num=3):
    flag, data = False, None
    headers = {'Authorization': PIPELINE_TOKEN_FOREVER}
    while try_num > 0:
        try:
            res = requests.get(uri, params=params, timeout=TIMEOUT, headers=headers)
            res = res.json()
            if res.get('status'):
                logging.info('deploy to %s succeed' % uri)
                flag, data = True, res.get('data')
                break
            else:
                msg = res['message']
                logging.info('deploy to %s failed, the reason is %s' % (uri, msg))
                try_num -= 1
        except Exception as e:
            logging.error(e)
            traceback.print_exc()
            try_num -= 1

        time.sleep(10)

    if flag is False:
        sys.exit(1)
    logging.info('response: {}'.format(data))
    return data

def load_module(pyfile):
    '''动态加载模块

    `pyfile`: py脚本绝对路径, /xxx/script.py
    '''
    pyfile = pyfile.rstrip('.py')
    py_dir = os.path.dirname(pyfile)
    sys.path.append(py_dir)
    prefix = os.path.basename(pyfile)  # 不能含有.py的后缀即不能是文件
    return importlib.import_module(prefix)