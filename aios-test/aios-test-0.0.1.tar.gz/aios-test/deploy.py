# -*- coding: utf-8 -*-
"""aios evaluate
"""
import os
import sys
import json
import logging
from aios.utils.utils import PIPELINE_TOKEN_FOREVER, try_to_request

__all__ = ['deploy']

TENANT_ID = os.getenv('TENANT_ID')
CLASSES = os.getenv('CLASSES')
IMAGE_SHAPE = os.getenv('IMAGE_SHAPE', '32,32')
CP_SVC_URI = os.getenv('CP_SVC_URI')
MODEL_INFO = os.getenv('MODEL_INFO')
POST_DATA = os.getenv('POST_DATA')
MODEL_TYPE = os.getenv('MODEL_TYPE')

# 校验：模块加载的时候从环境变量中获取参数
def _check_env():
    logging.info('eval:参数校验...')
    assert TENANT_ID is not None, 'TENANT_ID(企业id)不能为空!'
    assert CLASSES is not None, 'CLASSES(类别)不能为空!'
    assert CP_SVC_URI is not None, 'CP_SVC_URI(CP部署服务url)不能为空!'
    assert POST_DATA is not None, 'POST_DATA(CP部署服务url参数)不能为空!'
    assert MODEL_INFO is not None, 'MODEL_INFO(模型目录)不能为空!'
    assert MODEL_TYPE is not None, 'MODEL_TYPE(模型类型)不能为空!'

def _get_model_real_path(model_folder):
    model_prefix = None
    load_epoch = None
    for it in os.listdir(model_folder):
        if it.endswith("params"):
            load_epoch = int(it[-11:-7])
            model_prefix = os.path.join(model_folder, it[0:-len('-0000.params')])
            break
    if not model_prefix:
        return False, "params file or json file not found", ""
    return True, model_prefix, load_epoch

def deploy():
    """参数传递考虑了两种方式，一是arg_parse, 另外是**kwargs
    """
    try:
        logging.info('start deploy action ....')
        
        data = json.loads(POST_DATA)
        model_prefix = None
        load_epoch = 0
        logging.info('post data is :')
        logging.info(data)
        if MODEL_TYPE in ['evaluate', 'active_learning']:
            # eval之后才deploy，判断evaluate的结果
            if not os.path.exists(MODEL_INFO):
                logging.info('record file not exist')
                sys.exit(1)

            with open(MODEL_INFO) as fo:
                ret = fo.readlines()
                if len(ret) != 3:
                    logging.info('evaluate result is not correct')
                    sys.exit(1)
                if ret[2].strip() == '1':  # 是否更新的标志位
                    model_folder = ret[0].strip()  # 换行符的处理
                    flag, model_prefix, load_epoch = _get_model_real_path(model_folder)
        else:
            # 直接进入到deploy
            model_prefix = MODEL_INFO

        if model_prefix:
            logging.info('model prefix is : %s' % model_prefix)
            cmd = 'python3 /app/tptool/tp_tool_deploy.py --script-path {} --mparser-model-prefix {} --mparser-load-epoch {} --classes {} --image-shape {}'.\
                format(data['containers'][0]['script_path'], model_prefix, load_epoch, CLASSES, IMAGE_SHAPE)   # @TODO --classes如果传的json字符串会解析出错
            if data['containers'][0]['sub_param']:
                cmd += ' --sub-param={}'.format(data['containers'][0]['sub_param'])
            if POST_DATA:
                cmd += ' --config %s' % POST_DATA
            logging.info('cmd is: %s' % cmd)
            data['containers'][0]['cmd'] = cmd
            try_to_request(CP_SVC_URI, data, PIPELINE_TOKEN_FOREVER)

        else:
            logging.error('get model prefix failed')

    except Exception as err:
        logging.error('occured: {}'.format(str(err)))
        import traceback
        traceback.print_exc()
        sys.exit(1)