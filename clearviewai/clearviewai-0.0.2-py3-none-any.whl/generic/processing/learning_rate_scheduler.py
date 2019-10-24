import numpy as np

def step_decay(epoch, init_alpha=.01, factor=.5, drop_step=2):
    # initialize the base initial learning rate, drop factor, and
    # epochs to drop every

    # compute learning rate for the current epoch
    alpha = init_alpha * (factor ** np.floor((1 + epoch) / drop_step))

    # return the learning rate
    return float(alpha)