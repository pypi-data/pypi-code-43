# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from six import with_metaclass
from skydl.model.layers.old_layers import OldLayers


class SuperNet(with_metaclass(ABCMeta)):
    """
    由多个layer组成的网络
    usage:
    class MNISTTFNet(SuperTFNet):
        def __init__(self, name=None, parser_args=None):
            super().__init__(name, parser_args)
            self.conv1 = nn.Conv2d(1, 20, 5)
            self.conv2 = nn.Conv2d(20, 20, 5)

        def forward(self, x):
            super().forward(x)
            x = F.relu(self.conv1(x))
            return F.relu(self.conv2(x))
    """
    @property
    def parser_args(self):
        return self._parser_args

    def name(self):
        """
        子类可以重写该方法
        :return:
        # super().name()
        """
        return self._net_name if self._net_name else 'super_net'

    @property
    def model_proxy(self)->object:
        """
        model_proxy maybe None or keras.Model or torch.nn.Module
        子类可以重写该方法的返回值类型便于IDE找到对应的静态类. e.g.
        @property
        def model_proxy(self)->keras.Model:
            return self._model_proxy
        """
        return self._model_proxy

    def get_proxy(self):
        if self._model_proxy is None:
            return self
        return self._model_proxy

    def __init__(self, name=None, parser_args=None):
        """
        子类需要重写该方法
        :param name e.g. "mnist" 或 "gym_trading"
        # super().__init__(name, parser_args)
        """
        self._model_proxy = None
        self._net_name = name
        self._parser_args = parser_args

    @abstractmethod
    def forward(self, *input, **kwargs):
        """
        子类需要重写该方法
        目标函数，返回可以和target(label)对比的predict(logits)
        :param *input: tuple类型 input[0]->batch_x
        :param **kwargs: dict类型 kwargs.get("parser_args")->parser_args
        :return: result
        # super().forward(x)
        ......
        model = MNISTTFModel().build_network()
        result = model(batch_x)
        ......
        """
        # return self.call_hidden_layers(input[0], name=kwargs.get("name"))
        if len(input) < 1:  # for keras serving
            return self.call_hidden_layers(kwargs.get("inputs"), name="predict")
        return self.call_hidden_layers(input[0], name="predict")

    def __call__(self, *input, **kwargs):
        """
        model = MNISTTFModel().build_network()
        有了__call__方法就可以方便直接调用model(batch_x, parser_args=self.parser_args)方法
        来执行下面forward方法的内容
        :param input:
        :param kwargs:
        :return:
        """
        result = self.forward(*input, **kwargs)
        return result

    @abstractmethod
    def call_hidden_layers(self, _x, name="predict"):
        """
        子类可以重写该方法
        @:param name: predict节点名，便于model serving
        @see forward(input)
        """
        old_layers = OldLayers(self.parser_args)
        name = 'predict' if name is None else name
        if self.parser_args.model == 'cnn':
            predict = old_layers.cnn2_layers(_x, name=name)
        elif self.parser_args.model == 'keras_cnn':
            predict = old_layers.keras_cnn_layers(_x, name=name)
        elif self.parser_args.model == 'lstm':
            predict = old_layers.lstm_layers(_x, name=name)
        elif self.parser_args.model == 'bilstm':
            self.parser_args.num_hidden = 2
            predict = old_layers.bilstm_layers(_x, name=name)
        else:
            predict = None
        return predict

    # @autograph.convert()
    def huber_loss_just_for_test(a, tf_devices=None):
        import tensorflow as tf
        with tf_devices:
            if tf.abs(a) <= tf.constant(3.0):
                loss = a * a / 2.0
            else:
                loss = tf.constant(3.0) * (tf.abs(a) - tf.constant(3.0) / 2.0)
            return loss

    # @autograph.convert()
    @abstractmethod
    def compile_loss_metrics_optimizer_predict(self, _x, _y, _learning_rate=0.001, devices=[]):
        """
        子类可以重写该方法
        Define loss(cost) and optimizer
        ref: The art of regularization  https://greydanus.github.io/2016/09/05/regularization/
        https://github.com/greydanus/regularization
        TensorFlow with multiple GPUs https://jhui.github.io/2017/03/07/TensorFlow-GPU/
        [TensorFlow笔记] TensorArray解析 https://blog.csdn.net/guolindonggld/article/details/79256018
        AutoGraph converts Python into TensorFlow graphs  https://medium.com/tensorflow/autograph-converts-python-into-tensorflow-graphs-b2a871f87ec7
        @FIXME 后续将该函数纳入@autograph.convert()，以使多GPU的train的模型在serving后的Inference阶段即使没有GPU的机器上也能正确执行模型graph
        如果accuracy为None, 则可以返回default_accuracy = tf.constant(0)
        :param _x:
        :param _y:
        :param _learning_rate:
        :param devices: e.g. []
        :return:
        """
        import tensorflow as tf
        num_gpu = len(devices)
        losses = []
        correct_pred_total = []
        _predict = None
        if num_gpu > 1:
            '''
            @FIXME 注意该处需要修改成训练后的模型可以适配在任何设备上都能serving model。目前self.parser_args.use_cuda=True训练的模型在serving后的Inference会报错
            tf.split在batch_size=1时会出错
            先不显式控制GPU，让tensorflow自己控制GPU的数据处理
            '''
            # 单机多cpu训练
            X_A = tf.split(_x, num_gpu)
            Y_A = tf.split(_y, num_gpu)
            for gpu_id in range(num_gpu):
                with devices[gpu_id]:
                    with tf.variable_scope(tf.get_variable_scope(), reuse=tf.AUTO_REUSE):
                        _predict = self.forward(X_A[gpu_id])
                        target = Y_A[gpu_id]
                        cost = tf.nn.softmax_cross_entropy_with_logits_v2(logits=_predict, labels=target)
                        losses.append(cost)
                        # Evaluate model
                        correct_pred = tf.equal(tf.argmax(_predict, 1), tf.argmax(target, 1))
                        correct_pred_total.append(correct_pred)
            # losses = tf.convert_to_tensor(losses, dtype=tf.float32)
            loss = tf.reduce_mean(tf.concat(losses, axis=0))
            loss = tf.add_n([loss] + tf.get_collection(tf.GraphKeys.REGULARIZATION_LOSSES))
            tf.summary.scalar('loss', loss)
            # Evaluate model
            accuracy = tf.reduce_mean(tf.cast(tf.concat(correct_pred_total, axis=0), tf.float32))
            tf.summary.scalar('accuracy', accuracy)
        else:
            _predict = self.forward(_x)
            target = _y
            loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=_predict, labels=target))
            loss = tf.add_n([loss] + tf.get_collection(tf.GraphKeys.REGULARIZATION_LOSSES))
            tf.summary.scalar('loss', loss)
            correct_pred = tf.equal(tf.argmax(_predict, 1), tf.argmax(target, 1))
            accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))
            tf.summary.scalar('accuracy', accuracy)
        # #Important!, colocate_gradients_with_ops收集多卡GPU训练数据
        # optimizer = tf.train.AdamOptimizer(learning_rate=_learning_rate).minimize(loss, colocate_gradients_with_ops=True)
        # #用了下面这个optimizer后训练时间比上面的optimizer从23秒增加到了39秒
        import tensorflow.contrib.slim as slim
        optimizer = slim.learning.create_train_op(loss,
                                                  tf.train.AdamOptimizer(learning_rate=_learning_rate),
                                                  summarize_gradients=True,
                                                  colocate_gradients_with_ops=True)
        return loss, accuracy, optimizer, _predict

