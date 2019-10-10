# -*- coding: utf-8 -*-
"""aios dataset
"""
import os
import sys
import json
import moment
import logging
import datetime
import argparse
import mxnet as mx
import numpy as np
from pytz import timezone
from aios.utils.rec_pack import MultiProcessRecPack, SegmentationPack
from aios.utils.utils import *
from aios.utils.db_utils import *
from aios.utils.other import SyntheticDataIter
from aios.cls.dataset import DatasetClass

__all__ = ['dataset_list', 'load', 'get_dataset']

TP_DB_URL = os.getenv('TP_DB_URL')
DLP_DB_URL = os.getenv('DLP_DB_URL')
ASYNC_EXPORT_URL = os.getenv('ASYNC_EXPORT_URL', 'http://aios-dlp-python/api/v2/dataset_export_bg_async/operation')
DATASET_LIST_URL = os.getenv('DATASET_LIST_URL', 'http://aios-dlp-v1/api/intellif/importData/find?algorithm=classification&pageSize=100000')

FRAMEWORK = os.getenv('FRAMEWORK')
ALGORITHM_TYPE = os.getenv('ALGORITHM_TYPE')
MOUNT_PATH = os.getenv('MOUNT_PATH', '/datakubeflow')
IMAGE_SHAPE = os.getenv('IMAGE_SHAPE', '32,32')
DATASET_OUTPUT_PATH = os.getenv('DATASET_OUTPUT_PATH')
LABEL_FILTER = os.getenv('LABEL_FILTER')

TENANT_ID = os.getenv('TENANT_ID')
USER_ID = os.getenv('USER_ID')
USER_NAME = os.getenv('USER_NAME')

# 校验：模块加载的时候从环境变量中获取参数
def _check_env():
    logging.info('dataset:参数校验...')
    # assert TP_DB_URL is not None, 'TP_DB_URL(TP数据库连接字符串)不能为空!'
    # assert FRAMEWORK is not None, 'FRAMEWORK(数据集打包,框架)不能为空!'
    # assert ALGORITHM_TYPE is not None, 'ALGORITHM_TYPE(算法类型)不能为空!'
    # assert DATASET_OUTPUT_PATH is not None, 'DATASET_OUTPUT_PATH(数据集打包输出路径)不能为空!'
    # assert LABEL_FILTER is not None, 'LABEL_FILTER(数据集标签筛选)不能为空!'
    # assert TENANT_ID is not None, 'TENANT_ID(企业id)不能为空!'
    # assert USER_ID is not None, 'USER_ID(用户id)不能为空!'
    # assert USER_NAME is not None, 'USER_NAME(用户名称)不能为空!'
    result = []
    result.append(assert_true(TP_DB_URL is not None, 'TP_DB_URL:TP数据库连接字符串'))
    result.append(assert_true(FRAMEWORK is not None, 'FRAMEWORK:数据集打包,框架'))
    result.append(assert_true(ALGORITHM_TYPE is not None, 'ALGORITHM_TYPE:算法类型'))
    result.append(assert_true(DATASET_OUTPUT_PATH is not None, 'DATASET_OUTPUT_PATH:数据集打包输出路径'))
    result.append(assert_true(LABEL_FILTER is not None, 'LABEL_FILTER:数据集标签筛选'))
    result.append(assert_true(TENANT_ID is not None, 'TENANT_ID:企业id'))
    result.append(assert_true(USER_ID is not None, 'USER_ID:用户id'))
    result.append(assert_true(USER_NAME is not None, 'USER_NAME:用户名称'))
    return False not in result
        
def _add_data_args(parser):
    data = parser.add_argument_group('Data', 'the input images')
    data.add_argument('--data-train', type=str, help='the training data')
    data.add_argument('--data-train-idx', type=str, default='', help='the index of training data')
    data.add_argument('--data-val', type=str, help='the validation data')
    data.add_argument('--data-val-idx', type=str, default='', help='the index of validation data')
    data.add_argument('--rgb-mean', type=str, default='123.68,116.779,103.939',
                      help='a tuple of size 3 for the mean rgb')
    data.add_argument('--rgb-std', type=str, default='1,1,1',
                      help='a tuple of size 3 for the std rgb')
    data.add_argument('--pad-size', type=int, default=0,
                      help='padding the input image')
    data.add_argument('--fill-value', type=int, default=127,
                      help='Set the padding pixels value to fill_value')
    data.add_argument('--image-shape', type=str, 
                      help='the image shape feed into the network, e.g. (3,224,224)')
    data.add_argument('--num-classes', type=int, help='the number of classes')
    data.add_argument('--num-examples', type=int, help='the number of training examples')
    data.add_argument('--data-nthreads', type=int, default=4,
                      help='number of threads for data decoding')
    data.add_argument('--benchmark', type=int, default=0,
                      help='if 1, then feed the network with synthetic data')
    return data

def _add_data_aug_args(parser):
    aug = parser.add_argument_group(
        'Image augmentations', 'implemented in src/io/image_aug_default.cc')
    aug.add_argument('--random-crop', type=int, default=0,
                     help='if or not randomly crop the image')
    aug.add_argument('--random-mirror', type=int, default=0,
                     help='if or not randomly flip horizontally')
    aug.add_argument('--max-random-h', type=int, default=0,
                     help='max change of hue, whose range is [0, 180]')
    aug.add_argument('--max-random-s', type=int, default=0,
                     help='max change of saturation, whose range is [0, 255]')
    aug.add_argument('--max-random-l', type=int, default=0,
                     help='max change of intensity, whose range is [0, 255]')
    aug.add_argument('--min-random-aspect-ratio', type=float, default=None,
                     help='min value of aspect ratio, whose value is either None or a positive value.')
    aug.add_argument('--max-random-aspect-ratio', type=float, default=0,
                     help='max value of aspect ratio. If min_random_aspect_ratio is None, '
                          'the aspect ratio range is [1-max_random_aspect_ratio, '
                          '1+max_random_aspect_ratio], otherwise it is '
                          '[min_random_aspect_ratio, max_random_aspect_ratio].')
    aug.add_argument('--max-random-rotate-angle', type=int, default=0,
                     help='max angle to rotate, whose range is [0, 360]')
    aug.add_argument('--max-random-shear-ratio', type=float, default=0,
                     help='max ratio to shear, whose range is [0, 1]')
    aug.add_argument('--max-random-scale', type=float, default=1,
                     help='max ratio to scale')
    aug.add_argument('--min-random-scale', type=float, default=1,
                     help='min ratio to scale, should >= img_size/input_shape. '
                          'otherwise use --pad-size')
    aug.add_argument('--max-random-area', type=float, default=1,
                     help='max area to crop in random resized crop, whose range is [0, 1]')
    aug.add_argument('--min-random-area', type=float, default=1,
                     help='min area to crop in random resized crop, whose range is [0, 1]')
    aug.add_argument('--min-crop-size', type=int, default=-1,
                     help='Crop both width and height into a random size in '
                          '[min_crop_size, max_crop_size]')
    aug.add_argument('--max-crop-size', type=int, default=-1,
                     help='Crop both width and height into a random size in '
                          '[min_crop_size, max_crop_size]')
    aug.add_argument('--brightness', type=float, default=0,
                     help='brightness jittering, whose range is [0, 1]')
    aug.add_argument('--contrast', type=float, default=0,
                     help='contrast jittering, whose range is [0, 1]')
    aug.add_argument('--saturation', type=float, default=0,
                     help='saturation jittering, whose range is [0, 1]')
    aug.add_argument('--pca-noise', type=float, default=0,
                     help='pca noise, whose range is [0, 1]')
    aug.add_argument('--random-resized-crop', type=int, default=0,
                     help='whether to use random resized crop')
    return aug

def _add_fit_args(parser):
    """
    parser : argparse.ArgumentParser
    return a parser added with args required by fit
    """
    train = parser.add_argument_group('Training', 'model training')
    train.add_argument('--network', type=str,
                       help='the neural network to use')
    train.add_argument('--num-layers', type=int,
                       help='number of layers in the neural network, \
                             required by some networks such as resnet')
    train.add_argument('--gpus', type=str,
                       help='list of gpus to run, e.g. 0 or 0,2,5. empty means using cpu')
    train.add_argument('--kv-store', type=str, default='device',
                       help='key-value store type')
    train.add_argument('--num-epochs', type=int, default=100,
                       help='max num of epochs')
    train.add_argument('--lr', type=float, default=0.1,
                       help='initial learning rate')
    train.add_argument('--lr-factor', type=float, default=0.1,
                       help='the ratio to reduce lr on each step')
    train.add_argument('--lr-step-epochs', type=str,
                       help='the epochs to reduce the lr, e.g. 30,60')
    train.add_argument('--initializer', type=str, default='default',
                       help='the initializer type')
    train.add_argument('--optimizer', type=str, default='sgd',
                       help='the optimizer type')
    train.add_argument('--mom', type=float, default=0.9,
                       help='momentum for sgd')
    train.add_argument('--wd', type=float, default=0.0001,
                       help='weight decay for sgd')
    train.add_argument('--batch-size', type=int, default=32,
                       help='the batch size')
    train.add_argument('--disp-batches', type=int, default=20,
                       help='show progress for every n batches')
    train.add_argument('--model-prefix', type=str,
                       help='model prefix')
    train.add_argument('--save-period', type=int, default=1, help='params saving period')
    parser.add_argument('--monitor', dest='monitor', type=int, default=0,
                        help='log network parameters every N iters if larger than 0')
    train.add_argument('--load-epoch', type=int,
                       help='load the model on an epoch using the model-load-prefix')
    train.add_argument('--top-k', type=int, default=0,
                       help='report the top-k accuracy. 0 means no report.')
    train.add_argument('--loss', type=str, default='',
                       help='show the cross-entropy or nll loss. ce strands for cross-entropy, nll-loss stands for likelihood loss')
    train.add_argument('--test-io', type=int, default=0,
                       help='1 means test reading speed without training')
    train.add_argument('--dtype', type=str, default='float32',
                       help='precision: float32 or float16')
    train.add_argument('--gc-type', type=str, default='none',
                       help='type of gradient compression to use, \
                             takes `2bit` or `none` for now')
    train.add_argument('--gc-threshold', type=float, default=0.5,
                       help='threshold for 2bit gradient compression')
    # additional parameters for large batch sgd
    train.add_argument('--macrobatch-size', type=int, default=0,
                       help='distributed effective batch size')
    train.add_argument('--warmup-epochs', type=int, default=5,
                       help='the epochs to ramp-up lr to scaled large-batch value')
    train.add_argument('--warmup-strategy', type=str, default='linear',
                       help='the ramping-up strategy for large batch sgd')
    train.add_argument('--profile-worker-suffix', type=str, default='',
                       help='profile workers actions into this file. During distributed training\
                             filename saved will be rank1_ followed by this suffix')
    train.add_argument('--profile-server-suffix', type=str, default='',
                       help='profile server actions into a file with name like rank1_ followed by this suffix \
                             during distributed training')
    train.add_argument('--use-imagenet-data-augmentation', type=int, default=0,
                       help='enable data augmentation of ImageNet data, default disabled')
    return train

def _export_dataset(async_export_url: str, data_id: int, label_filter: str, algorithm_type: str):
    '''从指定API导出数据集

    `label_filter`: 
    >>> [['水果', '苹果'], ['水果', '香蕉']]
    '''
    # has_label: 0没有标签的数据，1是有该标签的数据
    label_filter = json.loads(label_filter)
    params = {
        'data_id': data_id,
        'has_label': 1,
        'clazz': label_filter,
        'algorithm_type': algorithm_type,
        'source': 'pipeline'
    }
    logging.info('start export dataset...')
    return try_to_request_async(async_export_url, params)

def _repack(data_id, is_none_tp_dataset):
    '''重新打包最新的数据集
    '''
    try:
        parent_dir = os.path.dirname(DATASET_OUTPUT_PATH)
        try:
            # 存在两个节点同时运行,其中一个会报错
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
        except Exception as e:
            logging.error(e)

        label_json, export_res = _export_dataset(ASYNC_EXPORT_URL, data_id, LABEL_FILTER, ALGORITHM_TYPE)
        absolute_label_json = os.path.join(MOUNT_PATH.rstrip('/'), label_json.lstrip('/')).replace('/', os.path.sep)
        if not os.path.exists(absolute_label_json):
            logging.error('File not exist, {}'.format(absolute_label_json))
            sys.exit(1)
        # 导出的json文件
        labels = json.load(open(absolute_label_json, mode='rb'))

        logging.info('framework:{}, type_:{}'.format(FRAMEWORK, ALGORITHM_TYPE))
        logging.info('start pack...')
        if FRAMEWORK == 'mxnet':
            if ALGORITHM_TYPE == 'segmentation':
                SegmentationPack(mount_path=MOUNT_PATH).create_segmentation_txt(DATASET_OUTPUT_PATH, labels)
            elif ALGORITHM_TYPE == 'classification':
                # 转换多标签，组合成单标签
                labels = convert_labels_multi_2_single(labels)
                MultiProcessRecPack(mount_path=MOUNT_PATH, image_shape=IMAGE_SHAPE).mxnet_multiprocess_handle(DATASET_OUTPUT_PATH, labels)
            else:
                MultiProcessRecPack(mount_path=MOUNT_PATH, image_shape=IMAGE_SHAPE).mxnet_multiprocess_handle(DATASET_OUTPUT_PATH, labels)
            # 打包完成之后，记录数据集信息，更新缓存
            time_now = moment.date(datetime.datetime.now(timezone('UTC'))).format("YYYY-MM-DD HH:mm:ss")
            # sql语法转化
            tag = 'NULL' if export_res.get('uuid') is None else "'{}'".format(export_res.get('uuid'))
            pack_pos = 'NULL' if DATASET_OUTPUT_PATH is None else "'{}'".format(DATASET_OUTPUT_PATH)

            if is_none_tp_dataset is False:
                name = export_res.get('dataset_name')
                tenant_id = export_res.get('tenant_id')
                sql = "insert into dataset_model(name, data_id, tag, tenant_id, pack_pos, created_by, created_at, owner) values('{}', {}, {}, {}, {}, {}, '{}', '{}');".format(name, data_id, tag, tenant_id, pack_pos, USER_ID, time_now, USER_NAME)
            else:
                sql = "update dataset_model set tag={}, pack_pos={}, updated_by={}, updated_at='{}' where data_id={};".format(tag, pack_pos, USER_ID, time_now, data_id)
            
            logging.info('更新TP数据库数据集记录...')
            execute(TP_DB_URL, sql)
            # red file
            return DATASET_OUTPUT_PATH
        else:
            logging.info('暂不支持的框架, {}'.format(FRAMEWORK))
            sys.exit(1)
    except Exception as err:
        logging.error('repack error, {}'.format(err))

def get_dataset(dataset_obj):
    '''获取数据集，从历史缓存获取/重新打包

    `Returns`:
    1. rec file
    '''

    # 检测数据集是否有变动
    tp_sql = 'select tag, pack_pos from dataset_model where data_id = {};'.format(dataset_obj.data_id)
    tp_dataset = query_one(TP_DB_URL, tp_sql)

    logging.info('dlp数据库中uuid:{}, tp数据库中tag:{}'.format(dataset_obj.tag, tp_dataset[0]))
    if tp_dataset is None or dataset_obj.tag != tp_dataset[0]:
        # 拉取最新数据集打包
        is_none_tp_dataset = bool(tp_dataset)
        rec_file = _repack(dataset_obj.data_id, is_none_tp_dataset)
        logging.info('拉取最新数据集打包')
    else:
        # 获取历史数据集recfile
        rec_file = tp_dataset.pack_pos
        logging.info('获取历史数据集recfile')
    
    return rec_file

def load(dataset_obj: DatasetClass, predicate=None):
    '''
    `Params`:  
        dataset_obj (DatasetClass): (cls.dataset).
        predicate (mixed): Predicate applied per iteration.

    `Return`: 
        Iter: Filtered rec iter.
    '''
    if not _check_env():
        return

    parser = argparse.ArgumentParser(description="train imagenet-1k",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    _add_fit_args(parser)
    _add_data_args(parser)
    _add_data_aug_args(parser)

    parser.set_defaults(
        # network
        network          = 'resnet',
        num_layers       = 50,
        # data
        num_classes      = 1000,
        num_examples     = 1281167,
        image_shape      = '3,32,32',
        min_random_scale = 1, # if input image has min size k, suggest to use
                              # 256.0/x, e.g. 0.533 for 480
        # train
        num_epochs       = 80,
        lr_step_epochs   = '30,60',
        dtype            = 'float32'
    )

    args = parser.parse_args()
    # 加载数据集
    data_train = get_dataset(dataset_obj)
    assert os.path.exists(data_train), '找不到rec文件, {}'.format(data_train)

    image_shape = (3,) + tuple([int(l) for l in IMAGE_SHAPE.split(',')])
    if 'benchmark' in args and args.benchmark:
        data_shape = (args.batch_size,) + image_shape
        train = SyntheticDataIter(args.num_classes, data_shape,
                args.num_examples / args.batch_size, np.float32)
        return (train, None)

    # rec file
    train = mx.io.ImageRecordIter(
        path_imgrec=data_train,
        path_imgidx='',
        label_width=1,
        preprocess_threads=args.data_nthreads,
        data_name='data',
        label_name='softmax_label',
        shuffle=True,
        data_shape=image_shape,
        batch_size=args.batch_size,
    )
    return train

def dataset_list():
    '''数据集列表函数，获取当前企业下所有数据集记录的列表
    '''
    _check_env()

    datasets = try_to_get_request(DATASET_LIST_URL, params={'algorithm': ALGORITHM_TYPE, 'pageSize': 100000})
    return [convert_dataset(dataset) for dataset in datasets]
