# -*- coding: utf-8 -*-
import tensorflow as tf
from tensorflow_estimator import estimator  # estimator import方便查看源代码
from skydl.model.default_estimator_net import DefaultEstimatorNet
from skydl.model.default_model import DefaultModel


class DefaultEstimatorModel(DefaultModel):
    """
    default estimator model implements
    要从编译的Keras模型创建Estimator，我们需要调用model_to_estimator方法。
    请注意，Keras模型的初始模型状态将保留在创建好Estimator中。
    那么Estimator有什么好处呢？那么开始：
    1.无需更改模型即可在本地主机或分布式多GPU环境中运行基于Estimator的模型；
    2.Estimator简化了模型开发人员之间的共享实现；
    3.Estimator为你构建了图，有点像Eager Execution，没有显式会话。
    """
    @property
    def model(self)->estimator.Estimator:
        """定义estimator.Estimator返回值类型便于IDE找到对应的静态类"""
        return self._model

    def __init__(self, name=None, layers=None, model_fn=None, params=None, loss=None, optimizer=None, metrics=None, weights=None):
        """参数model_fn返回的对象可以是keras.Model的subclass实例. 也可以是estimator.EstimatorSpec实例"""
        self._layers = layers
        self._model_fn = model_fn
        self._params = params
        super().__init__(name=name, loss=loss, optimizer=optimizer, metrics=metrics, weights=weights)

    def build_network(self):
        return DefaultEstimatorNet(self.name if self.name else self.__class__.__name__, self.parser_args,
                                   self._layers, self._model_fn, self._params)

    def load_data(self):
        pass

    def compile(self, loss=None, optimizer=None, metrics=None):
        self.loss = loss
        self.optimizer = optimizer
        self.metrics = metrics
        super().compile(loss=self.loss, optimizer=self.optimizer, metrics=self.metrics)
        # restore weights from latest checkpoint
        latest_checkpoint = tf.train.latest_checkpoint(self.get_model_checkpoint_dir())
        if latest_checkpoint:
            self.model.load_weights(latest_checkpoint)
        return self

    def fit(self):
        return self

    def evaluate(self, evaluate_dataset=None):
        return self

    def serving(self):
        return self

