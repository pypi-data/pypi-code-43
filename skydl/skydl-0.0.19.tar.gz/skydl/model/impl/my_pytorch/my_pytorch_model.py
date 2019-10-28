# -*- coding: utf-8 -*-
from skydl.datasets.pytorch_dataset_from_tf_datasets import PytorchDatasetFromTfDatasets
from skydl.model.impl.my_pytorch.my_pytorch_net import MyPyTorchNet
from skydl.model.super_torch_model import SuperTorchModel
from py_common_util.common.date_utils import DateUtils
import torch
import torch.optim as optim
from skydl.model.train_phase_enum import TrainPhaseEnum
from torch.autograd import Variable
from torchvision import datasets, transforms
import os, sys, datetime


class MyPyTorchModel(SuperTorchModel):

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
        self.parser_args.keep_prob = 0.25

    def build_network(self):
        return MyPyTorchNet(self.name if self.name else self.__class__.__name__, self.parser_args).to(self.device)

    def load_data(self):
        # Data loaders
        kwargs = {'num_workers': 1, 'pin_memory': True} if self.parser_args.use_cuda else {}
        train_loader = torch.utils.data.DataLoader(
            datasets.MNIST(self.parser_args.data_path + "/" + self.model.name(), train=True, download=True,
                           transform=transforms.Compose([
                               transforms.ToTensor(),
                               transforms.Normalize((0.1307,), (0.3081,))
                           ])),
            batch_size=self.parser_args.batch_size, shuffle=True, **kwargs)
        test_loader = torch.utils.data.DataLoader(
            datasets.MNIST(self.parser_args.data_path + "/" + self.model.name(), train=False, download=True, transform=transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize((0.1307,), (0.3081,))
            ])),
            batch_size=1000, shuffle=True, **kwargs)
        return train_loader, test_loader

    def load_data_new(self):
        datasets = {split: PytorchDatasetFromTfDatasets(tf_dataset_class="mnist",
                                                        all_datasets=["all"],
                                                        batch_size=128,
                                                        shuffle=1,
                                                        epochs=1,
                                                        train_size=0.7,
                                                        validation_size=0,
                                                        test_size=0.2,
                                                        selected_split=split) for split in ["train", "test"]}
        return datasets

    def fit(self):
        train_data, test_data = self.load_data()
        valid_data = test_data  # xxx
        start_time_int = DateUtils.now_to_int()
        print('[' + self.model.name() + ']==>>> total training batch number: {}'.format(len(train_data)))
        print('[' + self.model.name() + ']==>>> total validation batch number: {}'.format(len(valid_data)))
        print('[' + self.model.name() + ']==>>> total testing batch number: {}'.format(len(test_data)))
        print(self.model.name() + ", begin to fitting model, Time: {}".format(datetime.datetime.now()))
        optimizer = optim.SGD(self.model.parameters(), lr=self.parser_args.learning_rate, momentum=self.parser_args.momentum)
        for epoch in range(1, self.parser_args.epochs + 1):
            self.model.do_train_from_numpy_data(self.model, self.device, train_data, len(train_data), optimizer, epoch)
            self.model.do_train_from_numpy_data(self.model, self.device, valid_data, len(test_data), optimizer, epoch)
            self.model.do_test_from_numpy_data(self.model, self.device, test_data, len(test_data))

        self.export_to_onnx(self.model, [1,28,28])
        print('finished training, it took times(seconds): %d' % DateUtils.calc_duration_seconds(start_time_int, DateUtils.now_to_int()))

    def fit_new(self):
        datasets = self.load_data()
        train_data = datasets["train"]
        test_data = datasets["test"]
        valid_data = test_data  # xxx
        start_time_int = DateUtils.now_to_int()
        print('[' + self.model.name() + ']==>>> total training batch number: {}'.format(len(train_data)))
        print('[' + self.model.name() + ']==>>> total validation batch number: {}'.format(len(valid_data)))
        print('[' + self.model.name() + ']==>>> total testing batch number: {}'.format(len(test_data)))
        print(self.model.name() + ", begin to fitting model, Time: {}".format(datetime.datetime.now()))
        optimizer = optim.SGD(self.model.parameters(), lr=self.parser_args.learning_rate, momentum=self.parser_args.momentum)
        for epoch in range(1, self.parser_args.epochs + 1):
            self.model.do_train_from_numpy_data(self.model, self.device, train_data, len(train_data), optimizer, epoch)
            self.model.do_train_from_numpy_data(self.model, self.device, valid_data, len(test_data), optimizer, epoch)
            self.model.do_test_from_numpy_data(self.model, self.device, test_data, len(test_data))

        self.export_to_onnx(self.model, [1,28,28])
        print('finished training, it took times(seconds): %d' % DateUtils.calc_duration_seconds(start_time_int, DateUtils.now_to_int()))

    def evaluate(self, *args, **kwargs):
        pass

    def serving(self):
        pass

    def predict(self, *args, **kwargs):
        pass

    def export_to_onnx(self, model, input_shape_channel_height_width):
        """
        save model and export to onnx
        :param model 继承SuperPytorchNet(nn.Module)
        :param input_channel_height_width_shape 为model(input)的input的shape e.g. 【1, 28, 28】
        :return:
        """
        export_path = self.parser_args.onnx_export_path + "/" + model.name()
        if not os.path.exists(export_path):
            os.makedirs(export_path)
        torch.save(model.state_dict(), export_path + "/" + model.name())
        print('The model was saved to: ' + export_path + "/" + model.name())
        model.eval()
        num_total = 1
        dummy_input = Variable(torch.randn(num_total, *input_shape_channel_height_width).zero_().to(self.device))
        torch.onnx.export(model, dummy_input, export_path + "/" + model.name() + ".onnx.pb", verbose=False)
        print('The model was exported to: ' + export_path + "/" + model.name() + ".onnx.pb")



