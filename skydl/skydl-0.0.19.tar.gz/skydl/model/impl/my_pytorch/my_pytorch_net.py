# -*- coding: utf-8 -*-
import torch
import torch.nn as nn
import torch.nn.functional as F
from py_common_util.pytorch.torch_utils import TorchUtils
from torch.autograd import Variable
from skydl.model.super_torch_net import SuperTorchNet


class MyPyTorchNet(SuperTorchNet):

    def __init__(self, name=None, parser_args=None):
        super().__init__(name=name, parser_args=parser_args)
        self.conv1 = nn.Conv2d(1, 10, kernel_size=5)
        self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
        self.conv2_drop = nn.Dropout2d()
        self.fc1 = nn.Linear(320, 50)
        self.fc2 = nn.Linear(50, 10)
        # new net define
        # self.fc11 = nn.Linear(28 * 28, 500)
        # self.fc22 = nn.Linear(500, 256)
        # self.fc33 = nn.Linear(256, 10)

    def forward(self, *input, **kwargs):
        x = F.relu(F.max_pool2d(self.conv1(input[0]), 2))
        x = F.relu(F.max_pool2d(self.conv2_drop(self.conv2(x)), 2))
        x = x.view(-1, 320)
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)
        # new forward
        # x = input[0].view(-1, 28 * 28)
        # x = F.relu(self.fc11(x))
        # x = F.relu(self.fc22(x))
        # x = self.fc33(x)
        # return x

    def do_train_from_numpy_data(self, model, device, np_train_data, num_total, optimizer, epoch):
        """
        子类可以重写该方法
        :param args:
        :param model: SuperPytorchNet(nn.Module)
        :param device:
        :param train_loader:
        :param optimizer:
        :param epoch:
        :return:
        """
        self.train(True)
        for batch_idx, (data, label) in enumerate(np_train_data):
            # data, label = TorchUtils.np_to_tensor(data).to(device), torch.nn.functional.one_hot(TorchUtils.np_to_tensor(label)).to(device)
            data, label = TorchUtils.np_to_tensor(data).to(device), TorchUtils.np_to_tensor(label).to(device)
            # to avoid: CUDA error: out of memory
            data, label = Variable(data), Variable(label).long()
            optimizer.zero_grad()
            output = model(data)  # 调用SuperPytorchNet(nn.Module)的__call__方法, 执行net类的forward方法
            loss = F.cross_entropy(output, label).to(device)
            loss.backward()
            optimizer.step()
            if batch_idx % self.parser_args.log_interval == 0:
                print('Train Epoch: {} [{}/{} ({:.2f}%)]\tLoss: {:.6f}'.format(
                    epoch, batch_idx * len(data), num_total,
                           100.00 * batch_idx / num_total, loss.item()))

    def do_test_from_numpy_data(self, model, device, np_test_data, num_total):
        """
        子类可以重写该方法
        :param args:
        :param model:
        :param device:
        :param test_loader:
        :return:
        """
        self.eval()
        test_loss = 0
        correct = 0
        with torch.no_grad():
            for batch_idx, (data, label) in enumerate(np_test_data):
                data, label = TorchUtils.np_to_tensor(data).to(device), TorchUtils.np_to_tensor(label).to(device)
                # # to avoid: CUDA error: out of memory
                data, label = Variable(data), Variable(label).long()
                output = model(data)
                test_loss += F.nll_loss(output, label, reduction='sum').item()  # sum up batch loss
                pred = output.max(1, keepdim=True)[1]  # get the index of the max log-probability
                correct += pred.eq(label.view_as(pred)).sum().item()
        test_loss /= num_total
        print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.2f}%)\n'.format(
            test_loss, correct, num_total,
            100.00 * correct / num_total))

