# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
import tensorflow as tf
from six import with_metaclass
import numpy as np
from py_common_util.tensorflow.tf_utils import TFUtils
import argparse
import datetime, time
import os,sys
from logbook import Logger, StreamHandler, FileHandler
from collections import OrderedDict
from skydl.model.constants import Constants
from skydl.model.super_net import SuperNet
from skydl.model.train_phase_enum import TrainPhaseEnum
from py_common_util.common.common_utils import CommonUtils
sys.path.append(os.path.abspath('%s/..' % sys.path[0]))


class SuperModel(with_metaclass(ABCMeta)):
    """
    tf keras model
    class WideDeepKerasMode(DefaultKerasModel):
    定义model class：
    class XxxKerasModel(DefaultKerasModel):
        def adjust_parse_args_value(self):
            super().adjust_parse_args_value()
        def load_data(self, *args, **kwargs):
            super().load_data(*args, **kwargs)
        def fit(self, *args, **kwargs):
            return self
        def evaluate(self, *args, **kwargs):
            return self
        def serving(self, *args, **kwargs):
            return self
        def predict(self, *args, **kwargs):
            if not self.is_inference_phase():
                return None
            return None

    调用例子如下：
    from tensorflow.python import keras
    MyKerasModel("my_keras_model", [
        keras.layers.Flatten(input_shape=(28, 28)),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(128, activation='relu'),
        keras.layers.Dense(10, activation='softmax', name="prediction")
    ]).compile(
        keras.losses.sparse_categorical_crossentropy,
        keras.optimizers.Adam(),
        ['accuracy']
    ).fit().serving()
    ==========
    参考列表：
    https://www.tensorflow.org/alpha
    https://www.tensorflow.org/alpha/guide/saved_model#serving_the_model
    Training and Serving ML models with tf.keras  https://medium.com/tensorflow/training-and-serving-ml-models-with-tf-keras-fd975cc0fa27
    https://github.com/ray-project/ray/blob/master/python/ray/experimental/sgd/model.py
    https://colab.research.google.com
    将您的代码升级至 TensorFlow 2.0 https://mp.weixin.qq.com/s/BD-nJSZJLjBBq1n7HEHpKw
    tf2例子：https://github.com/tensorflow/docs/tree/master/site/en/r2/guide
    我的tf2训练场： https://colab.research.google.com/drive/1LtRP9lSivkdXJHX3S1_O8lFa9s21U6-V#scrollTo=ev01UBIHvaOj
    TensorFlow 2.0 Alpha 版发布啦！赶紧来尝鲜！https://mp.weixin.qq.com/s/gwcVOYhlEEBv28QoaFSnbw
    手工升级v1的代码到v2：$tf_upgrade_v2 --infile /Users/tony/myfiles/spark/share/python-projects/deep_trading/neural_networks/model/super_tf_model.py --outfile /Users/tony/myfiles/spark/share/python-projects/deep_trading/neural_networks/model/super_tf_model2.py
    """
    @property
    def log(self):
        return self._log

    @log.setter
    def log(self, value):
        self._log = value

    @property
    def parser(self):
        return self._parser

    @property
    def parser_args(self):
        return self._parser_args

    @property
    def num_gpu(self):
        return self._num_gpu

    @property
    def device(self):
        """
        gpu设备数组，多个设备表示为[tf.device(),tf.device()]
        为充分利用gpu, batch_size必须设置尽量大
        :return:
        usage:
        .........
        with self.device:
            sum_operation = tf.reduce_sum(dot_operation)
            ......
        """
        return self._device

    @property
    def name(self):
        return self._name

    @property
    def model(self)->SuperNet:
        """
        定义SuperNet返回值类型便于IDE找到对应的静态类
        子类可以重写该方法的返回值类型便于IDE找到对应的静态类. e.g.
        @property
        def model(self)->estimator.Estimator:
            return self._model
        """
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

    @property
    def loss(self):
        """Return loss of the model
        Returns:
            loss
        """
        return self._loss

    @loss.setter
    def loss(self, value):
        self._loss = value

    @property
    def optimizer(self):
        """Return optimizer for the model
        Returns:
            optimizer
        """
        return self._optimizer

    @optimizer.setter
    def optimizer(self, value):
        self._optimizer = value

    @property
    def metrics(self):
        """Return metrics of the model
        Returns:
            metrics(dict): e.g. {"accuracy": accuracy(numpy data)}
        """
        return self._metrics

    @metrics.setter
    def metrics(self, value):
        self._metrics = value

    @property
    def weights(self):
        """Return weights from the model.
        Implementing `get_weights` is required for checkpointing and fault
        tolerance.
        Returns:
            Numpy array of weights from the model.
        """
        return self._weights

    @weights.setter
    def set_weights(self, value):
        self._weights = value

    @property
    def latest_model_filename(self):
        return "model.ckpt"

    @property
    def distribute_strategy(self):
        """
        多GPU分布式训练策略
        e.g. print('Number of devices: {}'.format(self.distribute_strategy.num_replicas_in_sync))
        """
        return self._distribute_strategy

    def __init__(self, name=None, loss=None, optimizer=None, metrics=None, weights=None):
        super().__init__()
        StreamHandler(sys.stdout).push_application()
        self._name = name
        self._log = Logger(self.name if self.name else self.__class__.__name__)
        self._parser = argparse.ArgumentParser()
        self._parser_args = None
        self._device = None
        self._num_gpu = 0
        self.do_parse_args()
        self._model = None if self.parser_args.lazy_load_model else self.build_network()
        # loss, optimizer, metrics, weights
        self._loss = loss
        self._optimizer = optimizer
        self._metrics = metrics
        self._weights = weights
        # distribute strategy, e.g. tf.distribute.MirroredStrategy(devices=self.device)
        self._distribute_strategy = tf.distribute.MirroredStrategy()

    @abstractmethod
    def build_network(self):
        """
        子类需要重写该方法
        :return: a net of SuperTfNets
        # super().build_network()
        """
        return SuperNet(self.name if self.name else 'super_net', self.parser_args)

    def get_model_checkpoint_dir(self):
        model_checkpoint_dir = self.parser_args.model_checkpoint_path + "/" + self.model.name() + "/" + self.parser_args.model_version
        if not os.path.exists(model_checkpoint_dir):
            os.makedirs(model_checkpoint_dir)
        return model_checkpoint_dir

    def get_model_file_saved_dir(self):
        """
        整个model文件保存的目录：
        for keras, 使用如：
        ```
        # save mode to h5
        model.save(self.get_model_file_saved_dir() + "/saved_model.h5")
        # restore model from h5
        model = tf.keras.models.load_model(self.get_model_file_saved_dir() + "/saved_model.h5")
        ```
        :return:
        """
        model_file_saved_dir = "/tmp/super_model_file_saved_dir/" + self.model.name() + "/" + self.parser_args.model_version
        if not os.path.exists(model_file_saved_dir):
            os.makedirs(model_file_saved_dir)
        return model_file_saved_dir


    @abstractmethod
    def load_data(self):
        """
        load train|valid|test dataset
        子类需要重写该方法
        :return: lazy_load_data, iter_train_data_labels, total_train_batch, train data, test data, valid data, num_train_data, num_test_data, num_valid_data, input_shape_channel_height_width
        # super().load_data()
        """
        dict_load_data = OrderedDict()
        dict_load_data[Constants.DICT_LOAD_DATA_LAZY_LOAD_DATA] = False,
        dict_load_data[Constants.DICT_LOAD_DATA_ITER_TRAIN_DATA_LABELS] = tf.compat.v1.data.make_one_shot_iterator(tf.data.Dataset.range(1)),
        dict_load_data[Constants.DICT_LOAD_DATA_TOTAL_TRAIN_BATCH] = 0,
        dict_load_data[Constants.DICT_LOAD_DATA_NUM_TRAIN_DATA] = [],
        dict_load_data[Constants.DICT_LOAD_DATA_TEST_DATA] = [],
        dict_load_data[Constants.DICT_LOAD_DATA_VALIDATION_DATA] = [],
        dict_load_data[Constants.DICT_LOAD_DATA_NUM_TRAIN_DATA] = 0,
        dict_load_data[Constants.DICT_LOAD_DATA_NUM_TEST_DATA] = 0,
        dict_load_data[Constants.DICT_LOAD_DATA_NUM_VALIDATION_DATA] = 0,
        dict_load_data[Constants.DICT_LOAD_DATA_SHAPE_CHANNEL_HEIGHT_WIDTH] = (1, 28, 28)
        return dict_load_data

    def do_define_x_y(self):
        """子类可以重写该方法"""
        if self.parser_args.channels > 1:
            _x = tf.compat.v1.placeholder("float32", [None, self.parser_args.time_steps, self.parser_args.rnn_input, self.parser_args.channels])
        else:
            _x = tf.compat.v1.placeholder("float32", [None, self.parser_args.time_steps, self.parser_args.rnn_input])
        _y = tf.compat.v1.placeholder("int64", [None, self.parser_args.classes])
        return _x, _y

    def add_parser_argument(self):
        """
        增加parser参数项
        子类需要重写该方法
        # super().add_parser_argument()
        """
        self.parser.add_argument('--init_from_saver', type=bool, default=True, metavar='N',
                            help='init from saved checkpoint')
        self.parser.add_argument('--model_checkpoint_path', type=str, default=sys.path[0] + '/saved_model',
                            help='model checkpoint saved to path')
        self.parser.add_argument('--model_version', type=str, default='1',
                                 help='version number of the model')
        self.parser.add_argument('--train_phase', type=str, default=TrainPhaseEnum.Train.value,
                            help='train->train phase, test->test phase, inference->online inference phase, freeze->freeze model')
        self.parser.add_argument('--tf_summary_enabled', type=bool, default=False, metavar='N',
                            help='是否开启tensorflow的summary功能，注意在单机多GPU模式下开启该功能会让训练时间从24秒增加到107秒')
        self.parser.add_argument('--summary_path', type=str, default=sys.path[0] + '/summary',
                            help='dir where TensorBoard summary save to')
        self.parser.add_argument('--decay_rate', type=float, default=0.97, metavar='N',
                            help='decay rate for rmsprop, Decaying the learning rate)')
        self.parser.add_argument('--model', type=str, default='lstm',
                            help='value of "cnn|lstm|bilstm", if bilstm then should set--num-hidden=2 else --num-hidden=1')
        self.parser.add_argument('--channels', type=int, default=1, metavar='N',
                            help='channels (i.e. depth, default: 1)')
        self.parser.add_argument('--height', type=int, default=28,
                            help='height')
        self.parser.add_argument('--width', type=int, default=28,
                            help='width')
        self.parser.add_argument('--num_classes', type=int, default=10,
                            help='num of classes')
        self.parser.add_argument('--time_steps', type=int, default=28,
                            help="time steps num of RNN, default equals to height's value, also equals to seq_length")
        self.parser.add_argument('--rnn_input', type=int, default=28,
                            help="RNN input(the value as same as width)")
        self.parser.add_argument('--rnn_hidden', type=int, default=256,
                            help="num of RNN hidden_layer or state size, default value is multiple of batch_size's value")
        self.parser.add_argument('--num_hidden', type=int, default=1,
                            help="num of n_hidden, for RNN, default value is 1: using rnn.static_bidirectional_rnn")
        self.parser.add_argument('--keep_prob', type=float, default=0.5,
                                 help="dropout: keep probability, default value is: 0.5")
        # 以下变量和pytorch共用
        self.parser.add_argument('--data_path', type=str, default=sys.path[0] + '/dataset',
                            help='location of the loading data corpus')
        self.parser.add_argument('--onnx_export_path', type=str, default=sys.path[0] + '/saved_model',
                                 help='path to export the final model in onnx format')
        self.parser.add_argument('--batch_size', type=int, default=64, metavar='N',
                            help='input batch size for training (default: 64)')
        self.parser.add_argument('--eval_batch_size', type=int, default=1000, metavar='N',
                            help='input batch size for testing (default: 1000)')
        self.parser.add_argument('--epochs', type=int, default=1, metavar='N',
                            help='number of epochs to train (default: 10)')
        self.parser.add_argument('--learning_rate', type=float, default=0.001, metavar='LR',
                            help='learning rate (default: 0.001)')
        self.parser.add_argument('--momentum', type=float, default=0.5, metavar='M',
                            help='SGD momentum (default: 0.5)')
        self.parser.add_argument('--use_cuda', action='store_true', default=True,
                            help='use CUDA')
        self.parser.add_argument('--seed', type=int, default=1, metavar='S',
                            help='random seed (default: 1)')
        self.parser.add_argument('--log_interval', type=int, default=1000, metavar='N',
                            help='how many batches to wait before logging training status')
        self.parser.add_argument('--lazy_load_model', type=bool, default=False, metavar='N',
                             help='lazy load model(build_network())')

    def adjust_parse_args_value(self):
        """
        调整pare_args参数的值
        子类需要重写该方法
        修改parser_args的值
        # super().adjust_parse_args_value()
        e.g. self.parser_args.seed = 1
        参考代码：
        def adjust_parse_args_value(self):
            super().adjust_parse_args_value()
            self.parser_args.data_path = sys.path[0] + '/../../dataset'
            self.parser_args.use_cuda = True
            self.parser_args.init_from_saver = True
            self.parser_args.train_phase = TrainPhaseEnum.Train.value
            self.parser_args.model_version = '1'
            self.parser_args.epochs = 1
            self.parser_args.batch_size = 128
            self.parser_args.log_interval = 1000
        """
        pass

    def do_parse_args(self):
        self.add_parser_argument()
        self._parser_args = self.parser.parse_args()
        self.adjust_parse_args_value()
        # 设置random seed确保每次训练都可以获得相同唯一的的随机序列
        np.random.seed(self.parser_args.seed)
        tf.compat.v1.set_random_seed(self.parser_args.seed)
        self._num_gpu = TFUtils.check_available_gpus(show_info=True)
        if self.num_gpu > 0:
            if not self.parser_args.use_cuda:
                self.log.info("WARNING: You have " + str(self.num_gpu) + " CUDA device, so you should probably run with --cuda")
                # 不使用GPU加速
                self._num_gpu = 0
        else:
            self.parser_args.use_cuda = False
        if self.parser_args.use_cuda:
            self._device = [TFUtils.device("gpu" if self.parser_args.use_cuda else "cpu", gpu_id) for gpu_id in range(self._num_gpu)]
        else:
            self._device = []
        self.log.info("Tensorflow Version: " + tf.__version__ + "\nMain function argparse: " + str(self.parser_args))

    def is_training_phase(self):
        return self.parser_args.train_phase == TrainPhaseEnum.Train.value

    def is_evaluation_phase(self):
        return self.parser_args.train_phase == TrainPhaseEnum.Test.value

    def is_serving_phase(self):
        return self.parser_args.train_phase == TrainPhaseEnum.Serving.value

    def is_inference_phase(self):
        return self.parser_args.train_phase == TrainPhaseEnum.Inference.value

    def compile(self, loss=None, optimizer=None, metrics=None):
        """
        Configures the model for training
        compile a model before training/testing
        inference阶段不需要调用模型的compile函数
        @see keras.models.Model.compile()
        :param loss:
        :param optimizer:
        :param metrics:
        :return: self
        """
        if self.parser_args.lazy_load_model:
            self.model = self.build_network()
        return self

    @abstractmethod
    def fit(self, *args, **kwargs):
        """
        模型训练的启动入口
        子类需要重写该方法
        Training settings: 设置一些参数，每个都有默认值，输入 $python3 main.py -h 可以获得相关帮助
        $python3 main.py -batch_size=32 -log_interval=20
        :return: self
        """
        # kwargs = {'num_workers': 1, 'pin_memory': True} if self.parser_args.use_cuda else {}
        if self.parser_args.train_phase == TrainPhaseEnum.Freeze.value:
            # handle freeze model phase
            self.freeze_graph()
            return
        elif self.parser_args.train_phase == TrainPhaseEnum.Inference.value:
            return self.inference()
        # load train|valid|test dataset
        lazy_load_data, \
        iter_train_data_labels, \
        total_train_batch, \
        train_data, \
        valid_data, \
        test_data, \
        num_train_total, \
        num_valid_total, \
        num_test_total, \
        shape_channels_height_width = self.load_data()
        self.parser_args.channels, self.parser_args.height, self.parser_args.width = shape_channels_height_width
        self.log.info(self.model.name() + '==>>> lazy load data mode: {}'.format(lazy_load_data))
        self.log.info(self.model.name() + '==>>> total training batch number: {}'.format(total_train_batch))
        self.log.info(self.model.name() + '==>>> total validation batch number: {}'.format(len(valid_data)))
        self.log.info(self.model.name() + '==>>> total testing batch number: {}'.format(len(test_data)))
        self.log.info('[' + self.model.name() + ']begin to fitting model, Time: {}'.format(datetime.datetime.now()))
        with tf.compat.v1.name_scope('do_tf_training'):
            # add iter_train_data_labels to saver
            iter_batch_train_data_labels = iter_train_data_labels.get_next()
            saveable_obj_iterator = tf.data.experimental.make_saveable_from_iterator(iter_train_data_labels)
            tf.compat.v1.add_to_collection(tf.compat.v1.GraphKeys.SAVEABLE_OBJECTS, saveable_obj_iterator)
            # add learning_rate|epoch|step to saver
            train_learning_rate = tf.Variable(initial_value=0.0, trainable=False, dtype=tf.float32)
            curr_epoch_of_num_epoch = tf.Variable(initial_value=-1, trainable=False, dtype=tf.int32)
            curr_step_of_total_batch = tf.Variable(initial_value=-1, trainable=False, dtype=tf.int32)
            _x, _y = self.do_define_x_y()
            ###############
            # from tensorflow.contrib import autograph
            # tf_huber_loss = autograph.to_code(self.model.huber_loss_just_for_test)
            # print("tf_huber_loss, code==", tf_huber_loss)
            # # tf_huber_loss = autograph.to_graph(self.model.huber_loss_just_for_test)
            # # print("tf_huber_loss==", tf.Session().run(tf_huber_loss(tf.constant(12.0), self.device[0])))
            # # tf_do_loss_accuracy_optimizer_predict = autograph.to_code(self.model.do_loss_accuracy_optimizer_predict)
            # tf_do_loss_accuracy_optimizer_predict = autograph.to_code(self.model.do_loss_accuracy_optimizer_predict)
            # print("tf_do_loss_accuracy_optimizer_predict, code=", tf_do_loss_accuracy_optimizer_predict)
            # # print(autograph.to_code(self.model.do_loss_accuracy_optimizer_predict))
            ###############
            cost, accuracy, optimizer, predict = self.model.compile_loss_metrics_optimizer_predict(_x, _y, train_learning_rate, self.device)
            # allow_soft_placement=True: 如果指定的GPU设备不存在，允许TF自动分配CPU设备
            sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(allow_soft_placement=True, log_device_placement=False))
            init_op = tf.group(tf.compat.v1.global_variables_initializer(), tf.compat.v1.local_variables_initializer())  # sess.run(tf.tables_initializer())
            sess.run(init_op)
            saver = tf.compat.v1.train.Saver()
            try:
                start_time = time.time()
                if self.parser_args.train_phase == TrainPhaseEnum.Train.value:
                    # init_from_saver: True-从saved_model对应项目的缓存中拿上次的model结果作为起始参数，也可以手工删除saved_model对应项目的缓存文件以重新训练
                    if self.parser_args.init_from_saver:
                        checkpoint = tf.train.get_checkpoint_state(
                            self.get_model_checkpoint_dir(),
                            latest_filename=self.latest_model_filename)
                        if checkpoint and checkpoint.model_checkpoint_path:
                            saver.restore(sess, checkpoint.model_checkpoint_path)
                            self.log.info("Restored and Init Session Variables from Saver......")
                        else:
                            self.log.info("*** Error Occurred in " + self.parser_args.train_phase + " phase(1), Can not find the model file: "
                                + self.get_model_checkpoint_dir() + "/" + self.latest_model_filename)
                            self.log.info("And you can ignore this error, then the training will go on......")
                    self.log.info("TensorBoard Summary will Writing to {}".format(self.parser_args.summary_path))
                    self.log.info("Run the command line:\n" \
                          "--> tensorboard --logdir=" + self.parser_args.summary_path + "/../.." \
                          + "\nThen open http://0.0.0.0:6006/ into your web browser")
                    if self.parser_args.tf_summary_enabled:
                        tf_summary_writer = tf.compat.v1.summary.FileWriter(self.parser_args.summary_path, sess.graph)
                        merged_summary_op = tf.compat.v1.summary.merge_all()
                    from_step = sess.run(curr_step_of_total_batch) + 1
                    from_epoch = sess.run(curr_epoch_of_num_epoch)
                    self.log.info("init start: from_epoch_index=%d, from_step=%d" % (from_epoch, from_step))
                    if from_epoch < 0:
                        from_epoch += 1
                    else:
                        if from_step >= (total_train_batch - 1):
                            from_epoch += 1
                            from_step = 0
                    self.log.info("init end: from_epoch_index=%d, from_step=%d" % (from_epoch, from_step))
                    epoch_runnable = False
                    for epoch in range(from_epoch, self.parser_args.epochs):
                        self.log.info("begin to training data(%d), display_step: %d, epoch/(total): %d/%d ......"
                              % (num_train_total, self.parser_args.log_interval, epoch + 1, self.parser_args.epochs))
                        sess.run(curr_epoch_of_num_epoch.assign(epoch))
                        learning_rate = sess.run(tf.compat.v1.assign(train_learning_rate, self.parser_args.learning_rate * (self.parser_args.decay_rate ** epoch)))
                        total_cost = 0
                        if epoch > from_epoch:
                            from_step = 0
                        for step in range(from_step, total_train_batch):
                            epoch_runnable = True
                            batch_x, batch_y = sess.run(iter_batch_train_data_labels) if lazy_load_data else train_data[step]
                            batch_x, batch_y = self.do_transform_training_batched_data(batch_x, batch_y)
                            if not self.parser_args.tf_summary_enabled:
                                _, loss, acc = sess.run([optimizer, cost, accuracy],
                                                             feed_dict={_x: batch_x,
                                                                        _y: batch_y,
                                                                        train_learning_rate: learning_rate})
                            else:
                                merged_summarys, _, loss, acc = sess.run([merged_summary_op, optimizer, cost, accuracy],
                                                                         feed_dict={_x: batch_x,
                                                                                    _y: batch_y,
                                                                                    train_learning_rate: learning_rate})
                                tf_summary_writer.add_summary(merged_summarys, step)
                            total_cost += loss
                            if ((step + 1) % self.parser_args.log_interval == 0) or ((step + 1) >= total_train_batch):
                                sess.run(curr_step_of_total_batch.assign(step))
                                saver.save(sess,
                                           self.get_model_checkpoint_dir() + "/model.ckpt",
                                           global_step=epoch*total_train_batch+step,
                                           latest_filename="model.ckpt")
                                self.log.info("epoch+1/(total)/step+1/(total)/iter_data/(total): "
                                      + str(epoch + 1) + "/" + str(self.parser_args.epochs)
                                      + "/" + str(step + 1) + "/" + str(total_train_batch) + "/"
                                      + str((step + 1) * self.parser_args.batch_size) + "/" + str(num_train_total)
                                      + ", total_loss=" + "{:.6f}".format(total_cost)
                                      + ", training_accuracy=" + "{:.2f}%".format(100.00 * acc))
                    # save session after all training steps
                    if epoch_runnable:
                        saver.save(sess,
                                   self.get_model_checkpoint_dir() + "/model.ckpt",
                                   global_step=epoch*total_train_batch+step,
                                   latest_filename="model.ckpt")
                        tf.io.write_graph(sess.graph.as_graph_def(from_version=1),
                                             self.get_model_checkpoint_dir(),
                                             'graph.pbtxt',
                                             as_text=True)
                        self.log.info("saved model file to: " + self.parser_args.model_checkpoint_path + "/" + self.model.name())
                        # 统计整个训练时间
                        duration = (time.time() - start_time) * 1000
                        self.log.info("training Duration(milliseconds)=%d, Optimization Finished!" % duration)
                checkpoint = tf.train.get_checkpoint_state(
                    self.get_model_checkpoint_dir(),
                    latest_filename=self.latest_model_filename)
                if checkpoint and checkpoint.model_checkpoint_path:
                    saver.restore(sess, checkpoint.model_checkpoint_path)
                else:
                    self.log.info("*** Error For " + self.parser_args.train_phase
                          + " phase(2), can not find the model file: "
                          + self.get_model_checkpoint_dir() + "/" + self.latest_model_filename)
                    return
                self.log.info("Success to restore the model file for %s phase!" % self.parser_args.train_phase)
                if self.parser_args.train_phase == TrainPhaseEnum.Train.value or self.parser_args.train_phase == TrainPhaseEnum.Test.value:
                    self.log.info("Begin to Calculating Accuracy for all Test data(%d)......" % num_test_total)
                    start_time = time.time()
                    acc = self.do_test_from_numpy_data(sess, _x, _y, accuracy, test_data)
                    self.log.info("Done Test and the Test Accuracy is {:.2f}%".format(100.0*acc))
                    duration = (time.time() - start_time) * 1000
                    self.log.info(self.model.name() + ": for validate of " + self.parser_args.train_phase + " phase, Duration(milliseconds)=%d, Validate Finished!" % duration)
                    self.log.info("Now:" + str(datetime.datetime.now()))
                if self.parser_args.train_phase == TrainPhaseEnum.Train.value or self.parser_args.train_phase == TrainPhaseEnum.Serving.value:
                    self.build_serving_model(sess,
                                             _x, predict,
                                             self.get_model_checkpoint_dir())
            except:
                self.log.info('Error Occurred at trainning ' + self.model.name() + '......')
                import traceback
                traceback.print_exc()
            finally:
                pass
            return self

    @abstractmethod
    def evaluate(self, *args, **kwargs):
        """
        在测试阶段测试训练好的模型效果
        @:param evaluate_dataset:测试数据集, shape: [num_batched, batch_size, feature_size,label_size]
        :return: self
        ```
        usage:
         evaluate(evaluate_dataset=[]) then: evaluate_dataset = kwargs.get("evaluate_dataset")
         evaluate([]) then: evaluate_dataset = args[0])
        ```
        """
        return self

    @abstractmethod
    def serving(self):
        """
        build serving model
        用docker serving开启服务
        client可以使用java直接调用模型
        =====================
        https://www.tensorflow.org/alpha/guide/saved_model#serving_the_model
        java请求tensorflow-serving服务，返回模型结果  http://www.zhongruitech.com/222460444.html
        https://github.com/tobegit3hub/tensorflow_template_application/tree/master/java_predict_client
        使用Java客户端  http://docs.api.xiaomi.com/cloud-ml/modelservice/0903_use_java_client.html
        https://stackoverflow.com/questions/47196792/how-to-use-java-client-to-request-tensorflow-serving-for-widedeep-model-or-how
        构建 TensorFlow Serving Java 客户端  https://kaiyuanshuwu.com/articles/138
        =====================
        启动serving服务
        $docker run -p 8500:8500 -p 8501:8501 \
        --mount type=bind,source=/Users/tony/myfiles/spark/share/python-projects/deep_trading/skydl/examples/saved_model/serving/models/my_keras_model,target=/models/my_keras_model \
        -e MODEL_NAME=my_keras_model -t tensorflow/serving:1.13.0
        :return: self
        """
        return self

    @abstractmethod
    def predict(self, *args, **kwargs):
        """python版的预测接口，返回预测结果"""
        return None

    @CommonUtils.print_exec_time
    def inference(self, tfx_host_port="http://localhost:8501/", model_name=None, features_list=[]):
        """
        inference request to tf serving
        https://medium.com/tensorflow/serving-ml-quickly-with-tensorflow-serving-and-docker-7df7094aa008
        Deploy TensorFlow models https://towardsdatascience.com/deploy-tensorflow-models-9813b5a705d5
        #########################################
        $docker rmi -f <<old serving images>>
        $docker pull tensorflow/serving:1.13.0
        $docker run -p 8500:8500 -p 8501:8501 \
        --mount type=bind,source=/Users/tony/myfiles/spark/share/python-projects/deep_trading/skydl/examples/saved_model/serving/models/default_keras_net,target=/models/my_keras_model \
        -e MODEL_NAME=my_keras_model -t tensorflow/serving:1.13.0
        ########################################
        1.RESTful API https://www.tensorflow.org/tfx/serving/api_rest#model_metadata_api
        http://192.168.83.111:8501/v1/models/user_book_recommend/versions/1/metadata 或者 http://192.168.83.111:8501/v1/models/user_book_recommend/metadata
        2.A Java Client for TensorFlow Serving gRPC API https://medium.com/@junwan01/a-java-client-for-tensorflow-serving-grpc-api-d37b5ad747aa
        3.Tensorflow: save model for use in Java or C++  https://medium.com/@alexkn15/tensorflow-save-model-for-use-in-java-or-c-ab351a708ee4
        4.Saving and Loading a TensorFlow model using the SavedModel API  https://medium.com/@jsflo.dev/saving-and-loading-a-tensorflow-model-using-the-savedmodel-api-17645576527
        #########################################
        :param tfx_host_port: docker serving url, e.g. "http://localhost:8501/" 完整的post url，如"http://localhost:8501/v1/models/my_keras_model:predict"
        :param model_name: inference_model.model.name() e.g. "my_keras_model"
        :param features_list:  shape e.g. (1,28,28), 数据格式：tf_dataset_batched_features.tolist()[:100]
        features_list数据可以来自如下：
        _, evaluate_dataset = inference_model.load_data()
        import tensorflow_datasets as tfds
        for dataset in tfds.as_numpy(evaluate_dataset):
            features, labels = dataset
        features_list = features.tolist()
        ###用Postman工具调用的例子：
        #POST: http://192.168.83.111:8501/v1/models/user_book_recommend:predict
        Headers: {"content-type": "application/json"}
        Body(json):
        {
            "signature_name": "serving_default",
            "instances": [{"user_id":[0], "item_id":[260]}, {"user_id":[1], "item_id":[260]}]
        }
        Response:
        ```
        {
            "predictions": [
                [
                    1.50607
                ],
                [
                    3.53324
                ]
            ]
        }
        ```
        #GET: http://192.168.83.111:8501/v1/models/user_book_recommend/metadata
        Response:
        ```
        {
            "model_spec": {
                "name": "user_book_recommend",
                "signature_name": "",
                "version": "9"
            },
            "metadata": {
                "signature_def": {
                    "signature_def": {
                        "serving_default": {
                            "inputs": {
                                "user_id": {
                                    "dtype": "DT_FLOAT",
                                    "tensor_shape": {
                                        "dim": [
                                            {
                                                "size": "-1",
                                                "name": ""
                                            },
                                            {
                                                "size": "1",
                                                "name": ""
                                            }
                                        ],
                                        "unknown_rank": false
                                    },
                                    "name": "serving_default_user_id:0"
                                },
                                "item_id": {
                                    "dtype": "DT_FLOAT",
                                    "tensor_shape": {
                                        "dim": [
                                            {
                                                "size": "-1",
                                                "name": ""
                                            },
                                            {
                                                "size": "1",
                                                "name": ""
                                            }
                                        ],
                                        "unknown_rank": false
                                    },
                                    "name": "serving_default_item_id:0"
                                }
                            },
                            "outputs": {
                                "dense": {
                                    "dtype": "DT_FLOAT",
                                    "tensor_shape": {
                                        "dim": [
                                            {
                                                "size": "-1",
                                                "name": ""
                                            },
                                            {
                                                "size": "1",
                                                "name": ""
                                            }
                                        ],
                                        "unknown_rank": false
                                    },
                                    "name": "StatefulPartitionedCall:0"
                                }
                            },
                            "method_name": "tensorflow/serving/predict"
                        },
                        "__saved_model_init_op": {
                            "inputs": {},
                            "outputs": {
                                "__saved_model_init_op": {
                                    "dtype": "DT_INVALID",
                                    "tensor_shape": {
                                        "dim": [],
                                        "unknown_rank": true
                                    },
                                    "name": "NoOp"
                                }
                            },
                            "method_name": ""
                        }
                    }
                }
            }
        }
        ```
        :return:
        """
        import json
        import requests
        import traceback
        data = json.dumps({"signature_name": "serving_default",
                           "instances": features_list})
        headers = {"content-type": "application/json"}
        # 去掉url里最后一个/字符
        if tfx_host_port[-1] == '/':
            tfx_host_port = tfx_host_port[:-1]
        post_url = tfx_host_port + "/v1/models/" + model_name + ":predict"
        json_response = requests.post(post_url, data=data, headers=headers)
        print("the inference request takes times(milliseconds): " + str(json_response.elapsed.total_seconds()*1000))
        try:
            if not json_response.ok:
                self.log.info("the inference request failure, url: " + json_response.url + ", response code: " + str(json_response.status_code) + ", error reason: " + json_response.text)
                return []
            print("inference response json predictions：", json_response.json()["predictions"])
            print("inference response json predictions(删除掉单维度)：", np.squeeze(json_response.json()["predictions"]))
            prediction_list = np.array(json_response.json()["predictions"])
            print("inference response is ok, prediction_list after argmax is:" + str(tf.argmax(prediction_list, axis=1).numpy()))
            return prediction_list
        except:
            print("exception occured at an inference request!")
            traceback.print_exc()
        return []

    def build_serving_model(self,
                            sess=None,
                            _x=None,
                            predict=None,
                            model_checkpoint_path=None,
                            data_record_name=None,
                            model_version='1'):
        """
        TODO 该方法将被废弃
        #Serving Inception Model with TensorFlow Serving and Kubernetes https://www.tensorflow.org/serving/serving_inception
        #Improve TensorFlow Serving Performance With GPU Support https://docs.bitnami.com/google/how-to/enable-nvidia-gpu-tensorflow-serving/
        #tensorflow将训练好的模型freeze,即将权重固化到图里面,并使用该模型进行预测 https://blog.csdn.net/lujiandong1/article/details/53385092
        # A Tool Developer's Guide to TensorFlow Model Files https://www.tensorflow.org/extend/tool_developers/
        # How to EASILY put Machine Learning Models into Production using Tensorflow Serving
        https://medium.com/coinmonks/how-to-easily-put-machine-learning-models-into-production-using-tensorflow-serving-91998fa4b4e1
        # https://github.com/nex3z/tfserving-mnist
        # ref: https://www.tensorflow.org/serving/serving_basic
        # ref: https://github.com/tensorflow/serving/blob/master/tensorflow_serving/example/mnist_client.py
        https://hub.docker.com/r/tensorflow/serving/
        tensorflow教程6：Supervisor长期训练帮手  https://www.jianshu.com/p/7490ebfa3de8
        #########################################
        $docker rmi -f <<old serving images>>
        $docker pull tensorflow/serving:1.13.0
        $docker run -p 8500:8500 -p 8501:8501 \
        --mount type=bind,source=/tony/pycharm_projects/deep_trading/saved_model/serving/models/kcws,target=/models/kcws \
        -e MODEL_NAME=kcws -t tensorflow/serving:1.13.0
        """
        if model_checkpoint_path is None:
            model_checkpoint_path = self.parser_args.model_checkpoint_path + '/serving/models'
        if data_record_name is None:
            data_record_name = self.model.name()
        export_path_base = model_checkpoint_path + '/' + data_record_name
        export_path = os.path.join(
            tf.compat.as_bytes(export_path_base),
            tf.compat.as_bytes(model_version))
        self.log.info('exporting trained model to', str(export_path, 'utf-8'))
        if os.path.exists(export_path):
            self.log.info('......serving model saved path is already exists and please retry again，'
                  'you can remove the model path manually, command: rm -rf ' + str(export_path, 'utf-8'))
            return
        builder = tf.compat.v1.saved_model.builder.SavedModelBuilder(export_path)
        tensor_info_x = tf.compat.v1.saved_model.utils.build_tensor_info(_x)
        tensor_info_y = tf.compat.v1.saved_model.utils.build_tensor_info(predict)
        prediction_signature = (
            tf.compat.v1.saved_model.signature_def_utils.build_signature_def(
                inputs={'inputs': tensor_info_x},
                outputs={'scores': tensor_info_y},
                method_name=tf.saved_model.PREDICT_METHOD_NAME))
        """
        设置strip_default_attrs=Ture会保存graph里面的tf.data.one_shot_iterator()对象, 会导致启动serving的docker时出现如下异常：
        Invalid argument: Cannot add function 'tf_data_structured_function_wrapper_IcY4sd7IC5Q' because a different function with the same name already exists.
        """
        builder.add_meta_graph_and_variables(
            sess, [tf.saved_model.SERVING],
            signature_def_map={
                'prediction': prediction_signature
            },
            main_op=tf.compat.v1.tables_initializer(),
            strip_default_attrs=False)
        builder.save()
        self.log.info('done exporting serving model: ' + export_path_base)

    def export_to_onnx(self, model, input_shape_channel_height_width):
        """
        TODO 该方法将被废弃
        :param model 继承SuperTfNet(nn.Module)
        :param input_channel_height_width_shape 为model(input)的input的shape e.g. 【1, 28, 28】
        :return:
        """
        pass

    def freeze_graph(self, input_graph=None,
                     input_saver='',
                     input_binary=False,
                     input_checkpoint=None,
                     output_node_names='do_tf_training/LF/predict/MatMul',
                     restore_op_name='do_tf_training/save/restore_all',
                     filename_tensor_name='do_tf_training/save/Const:0',
                     output_graph=None,
                     clear_devices=True,
                     initializer_nodes='',
                     variable_names_blacklist=''):
        """
        TODO 该方法将被废弃
        子类可以重写该方法
        Converts all variables in a graph and checkpoint into constants
        参考：https://github.com/tensorflow/tensorflow/blob/master/tensorflow/python/tools/freeze_graph.py
        :param input_graph: TensorFlow \'GraphDef\' file to load.
        :param input_saver: TensorFlow saver file to load.
        :param input_binary: Whether the input files are in binary format.
        :param input_checkpoint: TensorFlow variables file to load.
        :param output_node_names: The name of the output nodes, comma separated.
        :param restore_op_name: The name of the master restore operator.
        :param filename_tensor_name: The name of the tensor holding the save path.
        :param output_graph: Output \'GraphDef\' file name.
        :param clear_devices: Whether to remove device specifications.
        :param initializer_nodes: comma separated list of initializer nodes to run before freezing.
        :param variable_names_blacklist: comma separated list of variables to skip converting to constants
        :return:
        """
        from google.protobuf import text_format
        from tensorflow.core.framework import graph_pb2
        from tensorflow.core.protobuf import saver_pb2
        from tensorflow.python.client import session
        from tensorflow.python.framework import graph_util
        from tensorflow.python.framework import importer
        from tensorflow.python.platform import gfile
        from tensorflow.python.training import saver as saver_lib

        if input_graph is None:
            input_graph = self.get_model_checkpoint_dir() + '/graph.pbtxt'
        if input_checkpoint is None:
            checkpoint = tf.train.get_checkpoint_state(self.get_model_checkpoint_dir(),
                                                       latest_filename="model.ckpt")
            if checkpoint:
                input_checkpoint = checkpoint.model_checkpoint_path
        if output_graph is None:
            output_graph = self.get_model_checkpoint_dir() + '/freezed-model.pbtxt'
        if not gfile.Exists(input_graph):
            self.log.info("Input graph file '" + input_graph + "' does not exist!")
            return -1

        if input_saver and not gfile.Exists(input_saver):
            self.log.info("Input saver file '" + input_saver + "' does not exist!")
            return -1

        # 'input_checkpoint' may be a prefix if we're using Saver V2 format
        if not saver_lib.checkpoint_exists(input_checkpoint):
            self.log.info("Input checkpoint '" + input_checkpoint + "' doesn't exist!")
            return -1

        if not output_node_names:
            self.log.info("You need to supply the name of a node to --output_node_names.")
            return -1

        input_graph_def = graph_pb2.GraphDef()
        mode = "rb" if input_binary else "r"
        with gfile.FastGFile(input_graph, mode) as f:
            if input_binary:
                input_graph_def.ParseFromString(f.read())
            else:
                # FIXED text_format.Merge(f.read().decode("utf-8"), input_graph_def)
                text_format.Merge(f.read(), input_graph_def)
        # Remove all the explicit device specifications for this node. This helps to
        # make the graph more portable.
        if clear_devices:
            for node in input_graph_def.node:
                node.device = ""
        _ = importer.import_graph_def(input_graph_def, name="")

        with session.Session() as sess:
            if input_saver:
                with gfile.FastGFile(input_saver, mode) as f:
                    saver_def = saver_pb2.SaverDef()
                    if input_binary:
                        saver_def.ParseFromString(f.read())
                    else:
                        text_format.Merge(f.read(), saver_def)
                    saver = saver_lib.Saver(saver_def=saver_def)
                    saver.restore(sess, input_checkpoint)
            else:
                sess.run([restore_op_name], {filename_tensor_name: input_checkpoint})
                if initializer_nodes:
                    sess.run(initializer_nodes)

            variable_names_blacklist = (variable_names_blacklist.split(",") if
                                        variable_names_blacklist else None)
            output_graph_def = graph_util.convert_variables_to_constants(
                sess,
                input_graph_def,
                output_node_names.split(","),
                variable_names_blacklist=variable_names_blacklist)
        with gfile.GFile(output_graph, "wb") as f:
            f.write(output_graph_def.SerializeToString())
        self.log.info("done freeze graph, %d ops in the final graph." % len(output_graph_def.node))

    def do_inference_from_freezed_model(self, freezed_model_path=None):
        """
        TODO 该方法将被废弃
        子类可以重写该方法
        :param freezed_model_path:
        :return:
        """
        return None

    def do_inference_from_saved_serving_model(self, np_x_input=None, model_name=None, hostport="localhost:8500"):
        """
        TODO 该方法将被废弃
        子类可以重写该方法
        :param np_x_input:
        :param model_name:
        :param hostport:
        :return:
        """
        import grpc
        from tensorflow_serving.apis import predict_pb2
        from tensorflow_serving.apis import prediction_service_pb2_grpc
        channel = grpc.insecure_channel(hostport)
        stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
        request = predict_pb2.PredictRequest()
        request.model_spec.name = model_name  # e.g. mnist
        request.model_spec.signature_name = 'serving_default'
        request.inputs['input_1'].CopyFrom(
            tf.compat.v1.make_tensor_proto(np_x_input, shape=np_x_input.shape))  # shape:e.g. [1,28,28,1]
        result_future = stub.Predict.future(request, 5.0)  # 5 seconds timeout
        exception = result_future.exception()
        if exception:
            self.log.info(exception)
        else:
            prediction = np.array(result_future.result().outputs['scores'].float_val)
            print("perdiction=", prediction)
            return prediction

