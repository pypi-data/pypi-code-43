# -*- coding: utf-8 -*-
"""aios models
"""
import os
import sys
import logging
import mxnet as mx
from aios.utils.db_utils import *
from aios.utils.utils import load_module
from aios.cls.model import ModelClass

__all__ = ['model_list', 'load']

TP_DB_URL = os.getenv('TP_DB_URL')
TENANT_ID = os.getenv('TENANT_ID')

def _check_env():
    # 校验：模块加载的时候从环境变量中获取参数
    logging.info('model:参数校验...')
    assert TP_DB_URL is not None, 'TP_DB_URL(TP数据库连接字符串)不能为空!'
    assert TENANT_ID is not None, 'TENANT_ID(企业id)不能为空!'

def _get_symbol(args):
    """
    :param args:
    :return:
    """
    args.depth = 50
    if args.format == 'python':
        model = load_module(args.prefix)

        # depth should be one of 110, 164, 1001,...,which is should fit (args.depth-2)%9 == 0
        if((args.depth-2)%9 == 0 and args.depth >= 164):
            per_unit = [(args.depth-2)/9]
            filter_list = [16, 64, 128, 256]
            bottle_neck = True
        elif((args.depth-2)%6 == 0 and args.depth < 164):
            per_unit = [(args.depth-2)/6]
            filter_list = [16, 16, 32, 64]
            bottle_neck = False
        else:
            raise ValueError("no experiments done on detph {}, you can do it youself".format(args.depth))
        units = per_unit*3
        symbol = model.resnet(units=units, num_stage=3, filter_list=filter_list, num_class=args.num_classes,
                        data_type="cifar10", bottle_neck=bottle_neck, bn_mom=args.bn_mom, workspace=args.workspace,
                        memonger=args.memonger)
        print(symbol)
        arg_params = None
        aux_params = None
    else:
        # 接着训练
        #symbol, _arg_params, aux_params = mx.model.load_checkpoint(args.prefix, args.model_load_epoch)

        # fine-tune, resnet.py一起上传，用reset.py获取模型结构，用与训练模型初始化参数
        from importlib import import_module
        try:
            model = import_module('resnet')
        except ModuleNotFoundError as err:
            raise Exception('找不到resnet模块，请检查是否已经上传，{}'.format(err))
        # depth should be one of 110, 164, 1001,...,which is should fit (args.depth-2)%9 == 0
        if((args.depth-2)%9 == 0 and args.depth >= 164):
            per_unit = [(args.depth-2)/9]
            filter_list = [16, 64, 128, 256]
            bottle_neck = True
        elif((args.depth-2)%6 == 0 and args.depth < 164):
            per_unit = [(args.depth-2)/6]
            filter_list = [16, 16, 32, 64]
            bottle_neck = False
        else:
            raise ValueError("no experiments done on detph {}, you can do it youself".format(args.depth))
        units = per_unit*3
        symbol = model.resnet(units=units, num_stage=3, filter_list=filter_list, num_class=args.num_classes,
                        data_type="cifar10", bottle_neck=bottle_neck, bn_mom=args.bn_mom, workspace=args.workspace,
                        memonger=args.memonger)

        # args.model_load_epoch是resume训练的时候用到，预训练的时候最好换个参数名
        __, _arg_params, aux_params = mx.model.load_checkpoint(args.prefix, args.model_load_epoch)
        arg_params = {}
        for key in _arg_params.keys():
            if key == 'fc1_bias' or key == 'fc1_weight':
                continue
            arg_params[key] = _arg_params[key]
    return symbol, arg_params, aux_params

def model_list():
    '''模型列表函数，获取当前企业下所有模型记录的列表
    '''
    _check_env()

    sql = 'select id, name, tenant_id, framework, type, path, origin, info, size, algorithm_type, version, format from model_model where tenant_id={} order by id asc;'.format(TENANT_ID)
    # convert to object
    models = query_many(TP_DB_URL, sql)
    return [convert_model(model) for model in models]

def load(model_obj: ModelClass):
    '''模型加载函数，模型分为多种格式：
    1. py文件
    2. params/json文件
    '''
    _check_env()
    
    assert model_obj.path is not None, 'model的path属性不能为空'
    assert os.path.exists(model_obj.path), 'model目录不存在'

    if model_obj.format == 'python':
        entry_module = None
        pyfiles = []
        for root, dirs, files in os.walk(model_obj.path):
            sys.path.append(root)
            for file in filter(lambda x: x.endswith('.py'), files):
                pyfiles.append(file)
        if len(pyfiles) >= 2 and 'main.py' not in pyfiles:
            raise Exception('错误的脚本，文件目录下找不到入口文件 main.py')
        entry_file = 'main.py' if 'main.py' in pyfiles else pyfiles[0]
        logging.info('加载python文件, {}'.format(entry_file))
        return load_module(entry_file[:-3])
    else:
        if model_obj.framework == "mxnet":
            params_file, symbol_json_file = None, None
            for it in os.listdir(model_obj.path):
                path = os.path.join(model_obj.path, it)
                if it.split(".")[-1] == "params":
                    params_file = path
                elif it.split(".")[-1] == "json":
                    symbol_json_file = path
            if not params_file or not symbol_json_file:
                raise Exception("params file or json file not found")

            model_obj.prefix = symbol_json_file[0: -len('-symbol.json')]
            model_obj.model_load_epoch = params_file[-11:-7]
            return _get_symbol(model_obj)
        else:
            raise Exception('不支持的framework, {}'.format(model_obj.framework))
