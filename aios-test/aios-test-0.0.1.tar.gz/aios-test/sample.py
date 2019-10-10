# -*- coding: utf-8 -*-
"""
    image classification training script, use cifa10 rec file, datashape is 3*32*32
    使用预训练模型fine-tune
"""

import logging
import mxnet as mx
import argparse
import os
import sys
import importlib

os.environ['MXNET_CUDNN_AUTOTUNE_DEFAULT'] = '0'

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',level=logging.INFO)
logging.info('start to train')


def log_train_metric(period, writer, auto_reset=False):
    """Callback to log the training evaluation result every period.
    inlucding tensorboard log and progress log
    period : int, The number of batch to log the training evaluation metric.
    auto_reset : bool, Reset the metric after each log.

    Returns
    -------
    callback : function
        The callback function that can be passed as iter_epoch_callback to fit.
    """
    def _callback(param):
        """The checkpoint function."""
        if param.nbatch % period == 0 and param.eval_metric is not None:
            name_value = param.eval_metric.get_name_value()
            for name, value in name_value:
                writer.add_scalar(name, value)
                logging.info('Iter[%d] Batch[%d] Train-%s=%f',
                             param.epoch, param.nbatch, name, value)
            if auto_reset:
                param.eval_metric.reset()

    return _callback

def start_train(args):
    """
    :param train_path:
    :param val_path:
    :param prefix: model preffix, only support symbol file,
    :param batch_size:
    :param epoch:
    :return:
    """

    train_path = args.train_data
    val_path = args.val_data
    batch_size = args.batch_size
    epoch = args.num_epochs
    
    [height, width] = args.image_shape.split(',')
    image_shape_width = int(width)
    image_shape_height = int(height)

    param_save_path = _get_model_save_path(args)

    logging.info('start_train')
    logging.info('params save path is %s' % param_save_path)
    logging.info('ImageRecordIter.data_shape is {}, {}'.format(image_shape_height, image_shape_width))
    devs = mx.cpu() if args.gpus is None or args.gpus == "" else [
        mx.gpu(int(i)) for i in args.gpus.split(',')]

    sym, arg_params, aux_params = _get_symbol(args)

    # load train data and test data
    train_data = mx.io.ImageRecordIter(
        path_imgrec=train_path,
        path_imgidx='',
        label_width=1,
        preprocess_threads=4,
        data_name='data',
        label_name='softmax_label',
        shuffle=True,
        data_shape=(3, image_shape_height, image_shape_width),
        batch_size=batch_size,
    )
    if val_path:
        val_data = mx.io.ImageRecordIter(
            path_imgrec=val_path,
            path_imgidx='',
            label_width=1,
            preprocess_threads=4,
            data_name='data',
            label_name='softmax_label',
            shuffle=True,
            data_shape=(3, image_shape_height, image_shape_width),
            batch_size=batch_size,
        )
    else:
        val_data = None

    mod = mx.mod.Module(
        symbol=sym, context=devs, label_names=(
            'softmax_label',), data_names=(
            'data',))
    data_shapes = train_data.provide_data

    mod.bind(
        for_training=True,
        data_shapes=data_shapes,
        label_shapes=train_data.provide_label)
    if arg_params is not None:
        mod.set_params(arg_params, aux_params, allow_missing=True)
    kv = mx.kv.create(args.kv_store)
    mod.fit(train_data,
            eval_data=val_data,
            num_epoch=epoch,
            kvstore=kv,
            epoch_end_callback=mx.callback.do_checkpoint(param_save_path),
            optimizer='sgd',
            optimizer_params={
                'learning_rate': 0.1,
                'wd': 0.0001,
                'momentum': 0.9,
                'multi_precision': True},
            eval_metric='acc',
            begin_epoch=0,
            )
    logging.info('finish train')

def _get_symbol(args):
    """
    :param args:
    :return:
    """
    args.depth = 50
    if args.model_type == 'python':
        py_dir = os.path.dirname(args.prefix)
        sys.path.append(py_dir)
        prefix = os.path.basename(args.prefix)  # 不能含有.py的后缀即不能是文件
        model = importlib.import_module(prefix)

        # depth should be one of 110, 164, 1001,...,which is should fit (args.depth-2)%9 == 0
        if ((args.depth - 2) % 9 == 0 and args.depth >= 164):
            per_unit = [(args.depth - 2) / 9]
            filter_list = [16, 64, 128, 256]
            bottle_neck = True
        elif ((args.depth - 2) % 6 == 0 and args.depth < 164):
            per_unit = [(args.depth - 2) / 6]
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
        model = import_module('resnet')
        # depth should be one of 110, 164, 1001,...,which is should fit (args.depth-2)%9 == 0
        if ((args.depth - 2) % 9 == 0 and args.depth >= 164):
            per_unit = [(args.depth - 2) / 9]
            filter_list = [16, 64, 128, 256]
            bottle_neck = True
        elif ((args.depth - 2) % 6 == 0 and args.depth < 164):
            per_unit = [(args.depth - 2) / 6]
            filter_list = [16, 16, 32, 64]
            bottle_neck = False
        else:
            raise ValueError("no experiments done on detph {}, you can do it youself".format(args.depth))
        units = per_unit*3
        symbol = model.resnet(units=units, num_stage=3, filter_list=filter_list, num_class=args.num_classes,
                        data_type="cifar10", bottle_neck=bottle_neck, bn_mom=args.bn_mom, workspace=args.workspace,
                        memonger=args.memonger)

        # args.model_load_epoch是resume训练的时候用到，预训练的时候最好换个参数名
        _, _arg_params, aux_params = mx.model.load_checkpoint(args.prefix, args.model_load_epoch)
        arg_params = {}
        for key in _arg_params.keys():
            if key == 'fc1_bias' or key == 'fc1_weight':
                continue
            arg_params[key] = _arg_params[key]
    return symbol, arg_params, aux_params

def _get_model_save_path(args):
    base_name = os.path.basename(args.output_path)
    param_save_path = os.path.join(args.output_path, base_name)
    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    return param_save_path

def _get_data_count(test_data):
    data_count = 0
    rec_reader = mx.recordio.MXRecordIO(test_data, 'r')
    while True:
        if not rec_reader.read():
            break
        data_count += 1
    rec_reader.close()

    return data_count

def _init_args():
    parser = argparse.ArgumentParser(description='train a model for image classification')
    parser.add_argument('--prefix', default='resnet', type=str, help='path to checkpoint prefix')
    parser.add_argument('--train-data', type=str, default="", help='training dataset')
    parser.add_argument('--val-data', type=str, default="", help='validation dataset')
    parser.add_argument('--model-load-epoch', type=int, default=0, help='resume model epoch')
    parser.add_argument('--model-type', type=str, default="python", help='json or py')
    parser.add_argument('--classes', type=str, help='label classes')
    parser.add_argument('--output-path', type=str, default="./models/fruit", help='')

    parser.add_argument('--image-shape', type=str, default='32,32', help='图片压缩尺寸')
    parser.add_argument('--batch-size', type=int, default=32, help='training batch size per device (CPU/GPU).')
    parser.add_argument('--optimizer', type=str, default='sgd', help='')
    parser.add_argument('--weight-decay', type=float, default=0.001, help='')
    parser.add_argument('--kv-store', type=str, default='local', help='key-value store type')
    parser.add_argument('--lr', type=float, default=0.01, help='learning rate. default is 0.1.')
    parser.add_argument('--lr-factor', type=float, default=1, help='')
    parser.add_argument('--lr-step-epochs', type=int, default=1, help='')
    parser.add_argument('--gpus', type=str, default=None, help="the gpu id str used for train, '0,1,2'")
    parser.add_argument('--num-epochs', type=int, default=10,help='number of training epochs.')
    parser.add_argument('--shuffle', action='store_true',help='default is false.')

    # optional
    parser.add_argument('--mom', type=float, default=0.9, help='momentum for sgd')
    parser.add_argument('--bn-mom', type=float, default=0.9, help='momentum for batch normlization')
    parser.add_argument('--workspace', type=int, default=512, help='memory space size(MB) used in convolution, if xpu '
                        ' memory is oom, then you can try smaller vale, such as --workspace 256')
    parser.add_argument('--depth', type=int, default=50, help='the depth of resnet')
    parser.add_argument('--num-examples', type=int, default=1281167, help='the number of training examples')
    parser.add_argument('--memonger', action='store_true', default=False,
                        help='true means using memonger to save momory, https://github.com/dmlc/mxnet-memonger')

    args = parser.parse_args()

    args.data_type = "cifar10"
    args.aug_level = 1  # use only random crop and random mirror
    
    # ===========================示例参数===========================
    args.train_data = '/datakubeflow/dev/tp/1/temp/run_pipeline/20190710003110a94d5dda/dataset/1021-a25f4d10-b7af-f097-ae37-c8fa6c207629.rec'
    args.val_data = '/datakubeflow/dev/tp/1/temp/run_pipeline/20190710003110a94d5dda/dataset/1021-daea0c4b-e2d2-76e9-e8a2-941abc067f13.rec'
    args.output_path = '/datakubeflow/dev/tp/1/temp/run_pipeline/20190710003110a94d5dda/model/12-c18f'
    args.classes = '"Apple Braeburn,Apple Crimson Snow,Apple Golden 1"'
    args.num_classes = len(args.classes.split(','))
    # fruit-resnet.py文件
    args.prefix = '/datakubeflow/dev/tp/3/6d219f54e85e8b6784847d13bf7a/fruit-resnet'
    args.model_type = 'python'
    args.model_load_epoch = 0
    # gpu序列, 0,1,2...
    args.gpus = '0'
    # 计算训练集数据量, 可以支持少量数据的调试和批量数据的作业
    # 可以固定指定大小
    args.batch_size = min(args.batch_size, _get_data_count(args.train_data))
    
    logging.info(args)
    return args

if __name__ == '__main__':
    args = _init_args()
    start_train(args)
