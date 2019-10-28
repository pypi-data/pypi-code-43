# -*- coding: utf-8 -*-
import torch
import argparse
from skydl.model.super_model import SuperModel
from py_common_util.pytorch.torch_utils import TorchUtils
import numpy as np
from skydl.model.super_torch_net import SuperTorchNet
from logbook import Logger, StreamHandler, FileHandler
import os, sys
sys.path.append(os.path.abspath('%s/..' % sys.path[0]))


class SuperTorchModel(SuperModel):
    """
    pytorch model
    在线教程：https://github.com/zergtant/pytorch-handbook
    pytorch中文教程网：https://www.pytorchtutorial.com/
    Pytorch Seq2Seq篇 https://fgc.stpi.narl.org.tw/activity/videoDetail/4b1141305df38a7c015e194f22f8015b
    """
    @property
    def model(self)->torch.nn.Module:
        """定义keras.Model返回值类型便于IDE找到对应的静态类"""
        return self._model

    def __init__(self, name=None, loss=None, optimizer=None, metrics=None, weights=None):
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
        self._distribute_strategy = None

    def add_parser_argument(self):
        """
        增加parser参数项
        子类需要重写该方法
        # super().add_parser_argument()
        """
        self.parser.add_argument('--data_path', type=str, default=sys.path[0] + '/dataset/wikitext_2',
                            help='location of the data corpus')
        self.parser.add_argument('--onnx_export_path', type=str, default=sys.path[0] + '/saved_model',
                                 help='path to export the final model in onnx format')
        self.parser.add_argument('--log_path', type=str, default=sys.path[0] + '/logs',
                            help='location of the loading data corpus')
        self.parser.add_argument('--batch_size', type=int, default=64, metavar='N',
                            help='input batch size for training (default: 64)')
        self.parser.add_argument('--eval_batch_size', type=int, default=1000, metavar='N',
                            help='input batch size for testing (default: 1000)')
        self.parser.add_argument('--epochs', type=int, default=1, metavar='N',
                            help='number of epochs to train (default: 10)')
        self.parser.add_argument('--learning_rate', type=float, default=0.01, metavar='LR',
                            help='learning rate (default: 0.01)')
        self.parser.add_argument('--momentum', type=float, default=0.5, metavar='M',
                            help='SGD momentum (default: 0.5)')
        self.parser.add_argument('--use_cuda', action='store_true', default=True,
                            help='use CUDA')
        self.parser.add_argument('--seed', type=int, default=1, metavar='S',
                            help='random seed (default: 1)')
        self.parser.add_argument('--log_interval', type=int, default=50, metavar='N',
                            help='how many batches to wait before logging training status')
        self.parser.add_argument('--lazy_load_model', type=bool, default=False, metavar='N',
                             help='lazy load model(build_network())')

    def do_parse_args(self):
        self.add_parser_argument()
        self._parser_args = self.parser.parse_args()
        self.adjust_parse_args_value()
        # 设置random seed确保每次训练都可以获得相同唯一的的随机序列
        np.random.seed(self.parser_args.seed)
        torch.manual_seed(self.parser_args.seed)
        self._num_gpu = TorchUtils.check_available_gpus(show_info=True)
        if self.num_gpu > 0:
            if not self.parser_args.use_cuda:
                self.log.info("WARNING: You have " + str(self._num_gpu) + " CUDA device, so you should probably run with --cuda")
                # 不使用GPU加速
                self._num_gpu = 0
        else:
            self.parser_args.use_cuda = False
        self._device = TorchUtils.device("gpu" if self.parser_args.use_cuda else "cpu")
        self.log.info("PyTorch Version: " + torch.__version__ + "\nMain function argparse: " + str(self.parser_args))

    def build_network(self):
        return SuperTorchNet(self.name if self.name else self.__class__.__name__, self.parser_args).to(self.device)

    def load_data(self):
        pass

    def fit(self):
        pass

    def evaluate(self, evaluate_dataset=None):
        pass

    def serving(self):
        pass

    def predict(self, *args, **kwargs):
        pass





