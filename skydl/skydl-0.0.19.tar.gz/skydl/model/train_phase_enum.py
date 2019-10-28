# coding: utf-8 or # -*- coding: utf-8 -*-
from enum import Enum, unique


@unique
class TrainPhaseEnum(Enum):
    """
    train->test->free|serving->inference
    TODO 注意：后面版本应该废弃free|serving中间状态
    """
    Train = 'train'  # train phase
    Test = 'test'  # test phase(i.e. evaluation phase)
    Freeze = 'freeze'  # freeze model(test之后，将graph中变量参数值固化成常量)
    Serving = 'serving'  # serving model(test之后，将模型预测能力对外暴露成API服务模式)
    Inference = 'inference'  # online inference phase


if __name__ == '__main__':
    for name, phase in TrainPhaseEnum.__members__.items():
        print(name, '=>', phase, ',', phase.value)
