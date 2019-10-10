# -*- coding: utf-8 -*-
"""aios training
"""
import os
import re
import sys
import logging
import argparse
import mxnet as mx
from aios.utils.db_utils import *
from aios.utils.utils import load_module, assert_true

__all__ = ['load_train_module']

TP_DB_URL = os.getenv('TP_DB_URL')
TENANT_ID = os.getenv('TENANT_ID')
TRAIN_OUTPUT_PATH = os.getenv('TRAIN_OUTPUT_PATH')
CLASSES = os.getenv('CLASSES')

PREFIX = os.getenv('PREFIX')
MODEL_TYPE = os.getenv('MODEL_TYPE')
MODEL_LOAD_EPOCH = os.getenv('MODEL_LOAD_EPOCH')

TRAIN_HYPER_PARAM = os.getenv('TRAIN_HYPER_PARAM')

# 校验：模块加载的时候从环境变量中获取参数
def _check_env():
    logging.info('train:参数校验...')
    # assert TP_DB_URL is not None, 'TP_DB_URL(TP数据库连接字符串)不能为空!'
    # assert TENANT_ID is not None, 'TENANT_ID(企业id)不能为空!'
    # assert TRAIN_OUTPUT_PATH is not None, 'TRAIN_OUTPUT_PATH(训练节点输出模型路径)不能为空!'
    # assert CLASSES is not None, 'CLASSES(类别)不能为空!'
    # 有可能不需要模型
    # assert PREFIX is not None, 'PREFIX(模型)不能为空!'
    # assert MODEL_TYPE is not None, 'MODEL_TYPE(模型类别)不能为空!'
    # assert MODEL_LOAD_EPOCH is not None, 'MODEL_LOAD_EPOCH(模型迭代次数)不能为空!'
    result = []
    result.append(assert_true(TP_DB_URL is not None, 'TP_DB_URL:TP数据库连接字符串'))
    result.append(assert_true(TENANT_ID is not None, 'TENANT_ID:企业id'))
    result.append(assert_true(TRAIN_OUTPUT_PATH is not None, 'TRAIN_OUTPUT_PATH:训练节点输出模型路径'))
    result.append(assert_true(CLASSES is not None, 'CLASSES:类别'))
    return False not in result

def load_train_module(train_script: str):
    '''加载训练脚本模块，训练函数是用训练模块自主调用并输出各项结果到TRAIN_OUTPUT_PATH中

    `Params`:
    1. train_script: 训练脚本绝对路径, 

    `Returns`:
    1. train_module: 以module的形式动态加载的训练脚本, 脚本中如果包含'set_args'函数, 则会执行
    '''
    if not _check_env():
        return

    parser = argparse.ArgumentParser(description="train", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    kwargs = {
        'output_path' : TRAIN_OUTPUT_PATH,
        'classes' : CLASSES
    }
    if PREFIX:
        kwargs['prefix'] = PREFIX
        kwargs['model_type'] = MODEL_TYPE
        kwargs['model_load_epoch'] = MODEL_LOAD_EPOCH
    
    if TRAIN_HYPER_PARAM:
        for i in re.findall(r'[--]*([^\s]\S*)\s+([^\s]\S*)', TRAIN_HYPER_PARAM):
            kwargs[i[0]] = i[1]
    parser.set_defaults(**kwargs)
    # 向训练脚本传递参数
    train_module = load_module(train_script)
    if hasattr(train_module, 'set_args'):
        train_module.set_args(parser.parse_args())
    else:
        logging.warning('训练脚本缺少\'set_args\'函数, 无法传入初始化参数!')

    return train_module
    
