# -*- coding: utf-8 -*-
from py_common_util.common.common_utils import CommonUtils
import sys
import os
from skydl.model.impl.my_pytorch.my_pytorch_model import MyPyTorchModel
sys.path.append(os.path.abspath('%s/..' % sys.path[0]))


@CommonUtils.print_exec_time
def run_default_model():
    MyPyTorchModel(
        "my_torch_model"
    ).compile(
    ).fit()


if __name__ == '__main__':
    run_default_model()














