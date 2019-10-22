import os, sys
from datetime import datetime
import keras
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import tqdm
import glob
import random

from keras.callbacks import ModelCheckpoint, LearningRateScheduler
try:
    from keras.applications import mobilenet_v2
except:
    from keras_applications import mobilenet_v2
from ailabtools.zaco import LabelTask
from ailabtools.keras.callbacks import TrainValTensorBoard
from ailabtools.keras.pairgenerator import PairDataGenerator
import ailabtools.statistic as st

def preprocess_image(x):
    x = x.astype(np.float32)
    x /= 127.5
    x -= 1.
    return x

def build_callbacks(model_name, base_log='.', base_lr=0.001):

    nowww = datetime.now()
    train_name = '{}_{}'.format(model_name, nowww.strftime("%Y-%m-%d_%H:%M:%S"))

    def check(path):
        if not os.path.exists(path):
            os.makedirs(path)
            
    base_log = os.path.join(base_log, train_name)
    log_dir = base_log+'/logs'
    train_dir = base_log+'/trains'
    
    check(base_log)
    check(log_dir)
    check(train_dir)

    def scheduler(epoch):
        drop_step = 5
        return base_lr*(0.9**(int(epoch/drop_step)))

    callbacks = [TrainValTensorBoard(log_dir=log_dir), 
                 ModelCheckpoint(train_dir
                                 +'/weights.{epoch:02d}-loss-{loss:.5f}-vloss-{val_loss:.5f}.hdf5', 
                                 monitor='val_loss', 
                                 verbose=1, 
                                 save_best_only=False),
                LearningRateScheduler(scheduler, verbose=1)]
    
    return callbacks

def _url_constructor(base_path, name_path, url_api='https://supplier.lab.zalo.ai/routing'):
    return os.path.join(url_api, base_path, name_path)

def _convert_data(db, url_constructor=None):
    if url_constructor == None:
        url_constructor = _url_constructor
    data = []
    for d in db:
        anno = d['annotations'][0]
        if anno['review']['rating'] >= 0:
            url = url_constructor(d['path']['base_path'], d['path']['server_path'])
            data.append([url, anno['class_id']])
    return data

def zaco_parser(annotation_path, classes=[], url_constructor=None):
    task = LabelTask(annotation_path)
    all_allocated_item = task.get_item_ids(class_ids=classes)
    all_allocated_item = task.get_items(all_allocated_item)
    dataset = _convert_data(all_allocated_item, url_constructor=url_constructor)
    random.shuffle(dataset)
    return dataset, task.classes

def train_zaco_classifier(anno_path, keep_classes=[], split=0.9, url_constructor=None, **kwargs):

    print('Parsing ZACO format...')
    dataset, class_map = zaco_parser(anno_path, classes=keep_classes, url_constructor=url_constructor)
    print('\tZACO classes:')
    for cls in keep_classes:
        print('\t\t{}: {}'.format(cls, class_map[cls]['name']))
    split_idx = int(len(dataset)*split)
    train_set = dataset[:split_idx]
    train_x = [a for a,_ in train_set]
    train_y = [a for _,a in train_set]
    print('\tNumber train set: {}'.format(len(train_x)))
    for cls in keep_classes:
        num = len([a for a in train_y if a==cls])
        print('\t\tNumber sample for class {}: {}'.format(cls, num))

    val_set = dataset[split_idx:]
    val_x = [a for a,_ in val_set]
    val_y = [a for _,a in val_set]
    print('\tNumber validation set: {}'.format(len(val_x)))
    for cls in keep_classes:
        num = len([a for a in val_y if a==cls])
        print('\t\tNumber sample for class {}: {}'.format(cls, num))
    print('Parsing ZACO format... DONE')

    return train_classifier((train_x, train_y), val_set=(val_x, val_y), **kwargs)

def parse_arg_param(**kwargs):
    default_aug_param = {
        'rotation_range': 10,
        'width_shift_range': 0.1, 
        'height_shift_range': 0.1, 
        'brightness_range': [0.7, 1.3], 
        'shear_range': 0.0, 
        'zoom_range': [0.8, 1.2], 
        'channel_shift_range': 0.2, 
        'horizontal_flip': True, 
        'vertical_flip': True,
    }
    setable_param = list(default_aug_param.keys())
    for k in setable_param:
        if k in kwargs:
            default_aug_param[k] = kwargs[k]
    return default_aug_param

def train_classifier(train_set, 
    model=None, 
    num_class=2,
    pre_channel=128,
    last_softmax=True,
    input_shape=(224,224,3),
    val_set=None, 
    model_name='classifier', 
    checkpoint_path='./log', 
    base_lr=0.01, 
    optimizer='sgd', 
    metrics=['accuracy'], 
    loss='categorical_crossentropy', 
    epoch=10, 
    batch_size=16,
    auto_construct_weight=True,
    num_worker=4,
    need_aug_data=True,
    mnet_alpha=1.0,
    **kwargs
):
    train_x, train_y = train_set

    # construct model
    print('Constructing model...')
    input = keras.layers.Input(input_shape)
    if model == None:
        print('\tNo specified model, using MobilenetV2 1.0 as default')
        backbone = mobilenet_v2.MobileNetV2(input_shape=input_shape, alpha=mnet_alpha, include_top=False, pooling=None)
        backbone_x = backbone(input)
        x = keras.layers.GlobalMaxPooling2D()(backbone_x)
        if pre_channel > 0:
            x = keras.layers.Dense(pre_channel, activation='relu', name='pre', kernel_initializer='he_normal')(x)
        x = keras.layers.Dense(num_class, activation='sigmoid', name='logits', kernel_initializer='he_normal')(x)
        if last_softmax:
            x = keras.layers.Softmax(name='output')(x)
        model = keras.models.Model(input, x, name=model_name)
    model.summary()
    print('Constructing model... DONE')

    print('Compiling model...')
    print('\tOptimizer: {}'.format(optimizer))
    print('\tLoss: {}'.format(loss))
    print('\tMetrics: {}'.format(metrics))
    model.compile(optimizer, loss=loss, metrics=metrics)
    print('Compiling model... DONE')

    print('Constructing generator...')
    if need_aug_data:
        aug_params = parse_arg_param(**kwargs)
        print('\tAugument param:')
        for k, v in aug_params.items():
            print('\t\t{}: {}'.format(k, v))
    else:
        aug_params = {}
    gen = PairDataGenerator(preprocessing_function=preprocess_image, **aug_params)
    gen_val = None
    if val_set is not None:
        gen_val = PairDataGenerator(preprocessing_function=preprocess_image)

    train_iter = gen.flow_from_pair(train_x, train_y, batch_size=batch_size, target_size=input_shape[:2], need_augmentation=need_aug_data)
    print('\tClass maping...')
    class_map = train_iter.class_indices
    for k, v in class_map.items():
        print('\t\tModel output {}: {}'.format(v, k))

    val_iter = None
    val_step = 0
    if val_set is not None:
        val_x, val_y = val_set
        val_iter = gen_val.flow_from_pair(val_x, val_y, batch_size=batch_size, target_size=input_shape[:2], need_augmentation=False)
        val_step = len(val_x)//batch_size+1
    print('Constructing generator... DONE')

    weights_dict_int = None
    if auto_construct_weight:
        print('Constructing class weights...')
        weights_dict = st.get_weight_dict(train_x, train_y, multiply=3)
        weights_dict_int = {}
        for k in weights_dict:
            weights_dict_int[class_map[int(k)]] = weights_dict[k]
            print('\tClass {}: {}'.format(k, weights_dict[k]))
        print('Constructing class weights... DONE')

    print('Constructing callbacks...')
    if not os.path.exists(checkpoint_path):
        os.makedirs(checkpoint_path)
    callbacks = build_callbacks(model_name, 
                        base_lr=base_lr, 
                        base_log=checkpoint_path)
    print('\tTo visualize training graph:')
    print('\t\ttensorboard --logdir={}'.format(checkpoint_path))
    print('Constructing callbacks... DONE')

    print('Start training process...')
    model.fit_generator(train_iter,
                    validation_data=val_iter,
                    epochs=epoch,
                    steps_per_epoch=len(train_x)//batch_size+1,
                    validation_steps=val_step,
                    class_weight=weights_dict_int, 
                    workers=num_worker, 
                    callbacks=callbacks,
                    use_multiprocessing=True)
    print('Start training process... DONE')

    return model

