# -*- coding: utf-8 -*-
"""aios evaluate
"""
import os
import re
import sys
import json
import shutil
import logging
import datetime
import argparse
import mxnet as mx
from aios.utils.db_utils import *
from aios.utils.utils import load_module, b64decode, b64encode, get_uniq_id

__all__ = ['evaluate_models']

TP_DB_URL = os.getenv('TP_DB_URL')
TENANT_ID = os.getenv('TENANT_ID')
FRAMEWORK = os.getenv('FRAMEWORK')
VAL_DATA = os.getenv('VAL_DATA')
EVAL_OUTPUT_PATH = os.getenv('EVAL_OUTPUT_PATH')
CLASSES = os.getenv('CLASSES')
ALGORITHM_TYPE = os.getenv('ALGORITHM_TYPE')
IMAGE_SHAPE = os.getenv('IMAGE_SHAPE', '32,32')

MODEL_ROOT = os.getenv('MODEL_ROOT')

EVAL_MODEL = os.getenv('EVAL_MODEL')
EVAL_SCRIPT = os.getenv('EVAL_SCRIPT')

GPUS = os.getenv('GPUS')

TENANT_ID = os.getenv('TENANT_ID')
USER_ID = os.getenv('USER_ID')
OWNER = os.getenv('OWNER')
ITER = os.getenv('ITER')

# 校验：模块加载的时候从环境变量中获取参数
def _check_env():
    logging.info('eval:参数校验...')
    assert TP_DB_URL is not None, 'TP_DB_URL(TP数据库连接字符串)不能为空!'
    assert TENANT_ID is not None, 'TENANT_ID(企业id)不能为空!'
    assert USER_ID is not None, 'USER_ID(用户id)不能为空!'
    assert OWNER is not None, 'OWNER(创建者)不能为空!'
    assert FRAMEWORK is not None, 'FRAMEWORK(框架)不能为空!'
    assert EVAL_OUTPUT_PATH is not None, 'EVAL_OUTPUT_PATH(训练节点输出模型路径)不能为空!'
    assert CLASSES is not None, 'CLASSES(类别)不能为空!'
    assert ALGORITHM_TYPE is not None, 'ALGORITHM_TYPE(算法类型)不能为空!'
    assert MODEL_ROOT is not None, 'MODEL_ROOT(模型目录)不能为空!'
    assert EVAL_MODEL is not None, 'EVAL_MODEL(待评估模型目录)不能为空!'
    assert EVAL_SCRIPT is not None, 'EVAL_SCRIPT(评估脚本)不能为空!'
    assert ITER is not None, 'ITER(迭代次数)不能为空!'

def _load_evaluate(function):
    """Get eavluate function from evaluation function file
    """
    eval_module = load_module(function.rstrip('.py'))
    return eval_module.evaluate

def _get_model_prefix_epoch(model_path):
    """Get all models in model path
    """
    epochs = []
    model_prefix = None
    for it in os.listdir(model_path):
        path = os.path.join(model_path, it)
        prefix, ext = os.path.splitext(path)
        if ext == ".params":
            epoch = prefix[-4:]
            if not epoch.isdigit():
                continue
            epoch = int(epoch)
            epochs.append(epoch)
            model_prefix = prefix[0:-len('-0000')]
        elif ext == ".json":
            model_prefix = prefix[0:len(prefix)-7]
    
    return model_prefix, epochs

def _save_result(model_prefix, flag, output_path, load_epoch=0):
    """Compare with previous iteration and write the result file
       保存到临时文件，供deploy和inference使用
       文件内容： 第一行,模型路径
                 第二行, load_epoch
                 第三行,0/1, 1表示比上次模型更优
    """
    result = model_prefix + "\n" + str(load_epoch) + "\n" + str(flag)
    file_path = output_path
    try:
        dir = os.path.dirname(file_path)
        if not os.path.exists(dir):
            os.mkdir(dir)
        # 所在目录要存在
        with open(file_path, "w") as f:  # 多此迭代如果目录相同会直接覆盖之前的结果
            f.write(result)
    except Exception as e:
        logging.error(e)
        return False, 'save result failed'
    return True, "Ok"

def _save_model(model_prefix, eval_value, save_epoch):
    """Save current best model to fs and db
        分三种情况py脚本第一次/预训练模型第一次/非第一次训练, 返回历史最优模型的model_prefix,load_epoch都是0
        确认现有的模型存储的接口，如果方便调用直接调用存储接口
        模型存储接口需要jwt认证；
    """
    logging.info('start to add new model to system %s' % model_prefix)
    # Save to fs, 每个json和params单独文件夹，文件夹名和json的前缀相同
    name = '_'.join([os.path.basename(model_prefix), str(ITER), get_uniq_id()])
    save_path = os.path.join(MODEL_ROOT, name)  # 文件夹目录
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    new_model_prefix = os.path.join(save_path, name)
    try:
        symbol_path = model_prefix + "-symbol.json"
        params_path = model_prefix + "-%04d.params" % save_epoch
        if os.path.exists(symbol_path):
            shutil.copy(symbol_path, "{}-symbol.json".format(new_model_prefix))
        # 如果要保留epoch信息，将0000修改为%04d
        shutil.copy(params_path, "{}-0000.params".format(new_model_prefix))
    except Exception as exception:
        logging.error(exception)
        return False, "Save model file failed"
    
    # Save to db
    origin = ""
    size_byte = os.path.getsize(params_path)
    if size_byte < 1024:
        size = str(size_byte) + 'B'
    elif size_byte < 1024 * 1024:
        size = '%.3f' % (size_byte / 1024) + 'KB'
    else:
        size = '%.3f' % (size_byte / (1024 * 1024)) + 'MB'
    info = {
        "iter": ITER,
        "eval_value": eval_value
    }
    try:
        path = os.path.dirname(new_model_prefix)
        sql = "INSERT INTO model_model( name, created_at, owner, created_by, tenant_id, format, framework," \
                  " type, path, origin, size, info) values('{}', '{}','{}','{}', '{}', '{}', '{}', '{}', '{}', '{}', " \
                  "'{}', '{}')".format(name, datetime.datetime.utcnow(), OWNER, USER_ID, TENANT_ID, format, FRAMEWORK,
                                       ALGORITHM_TYPE, path, origin, size, json.dumps(info))
        logging.info(sql)
        execute(TP_DB_URL, sql)
    except Exception as e:
        logging.error(e)
        return False, 'inser database error'

    # 返回model_prefix即数据库中的path,无文件后缀
    logging.info('add new model to system succeed')
    return True, path

def evaluate_models():
    """Eval all models generated by one training task, and save the best model
       评估之后新的模型命名后缀是0000.params,上传的预训练好的模型不一定是0000
    """
    try:
        # 评估脚本的参数
        eval_params = {}
        if ALGORITHM_TYPE == 'classification':
            eval_params['image_shape'] = IMAGE_SHAPE
        elif ALGORITHM_TYPE == 'segmentation':
            eval_params['gpus'] = GPUS
            eval_params['val_data'] = VAL_DATA
            eval_params['eval_'] = 'true'
        # 从指定路径解析模型名和epoch
        model_prefix, epoch_list = _get_model_prefix_epoch(EVAL_MODEL)
        # 从评估脚本加载评估接口
        evaluate_function = _load_evaluate(EVAL_SCRIPT)

        if not epoch_list:
            logging.error('model path has no params')
            sys.exit(1)

        logging.info('input model prefix is %s' % model_prefix)
        logging.info(epoch_list)

        # 逐个对模型做评估,找到当前训练轮中最优的
        index = -1
        max_value = -1

        logging.info(CLASSES)
        _classes = b64decode(CLASSES)
        logging.info('eval classes: {}'.format(_classes))
        # 改为只取最后一个checkpoint
        epoch_list.sort()
        new_epoch_list = [epoch_list[-1]]
        for i in range(0, len(new_epoch_list)):
            # 返回归一化数值用于比较
            value = evaluate_function(model_prefix=model_prefix, \
                                      load_epoch=new_epoch_list[i],
                                      test_data=VAL_DATA,
                                      classes=_classes, **eval_params)
            logging.info('eval output')
            logging.info(value)
            if not isinstance(value, (int, float)):
                logging.error('evaluate script return value illegal')
                sys.exit(1)

            if value >= max_value:
                max_value = value
                index = i

        if index < 0:
            logging.error('there is no model file in the folder')
            sys.exit(1)

        logging.info('the best model epoch in this iter is %s' % new_epoch_list[index])
        # 如果模型比上次优，保存到系统
        status, new_model_prefix = _save_model(model_prefix=model_prefix,
                                               save_epoch=new_epoch_list[index],
                                               eval_value=max_value)
        if not status:
            sys.exit(1)

        logging.info('return model prefix is %s' % new_model_prefix)
        flag = 0 if new_model_prefix == model_prefix else 1
        # 将结果保存到临时文件，用于下游节点使用
        status, message = _save_result(new_model_prefix, flag, EVAL_OUTPUT_PATH)
        if not status:
            sys.exit(1)
    except Exception as err:
        logging.error('occured: {}'.format(str(err)))
        import traceback
        traceback.print_exc()
        sys.exit(1)