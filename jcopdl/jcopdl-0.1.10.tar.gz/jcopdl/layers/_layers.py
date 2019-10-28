from torch import nn

_act_func = {
    "relu": nn.ReLU(),
    "lrelu": nn.LeakyReLU(),
    "sigmoid": nn.Sigmoid(),
    "tanh": nn.Tanh(),
    "elu": nn.ELU(),
    "selu": nn.SELU(),
    "softmax": nn.Softmax(1),
    "lsoftmax": nn.LogSoftmax(1)
}


def linear_block(n_in, n_out, batch_norm=False, activation='relu', dropout=0.):
    """
    available activation {relu, lrelu, sigmoid, tanh, elu, selu, softmax, lsoftmax}
    """
    layers = [nn.Linear(n_in, n_out)]

    if batch_norm:
        layers.append(nn.BatchNorm1d(n_out))

    if activation in _act_func:
        layers.append(_act_func[activation])
    else:
        raise Exception(f"jcopdl supports ({', '.join(_act_func.keys())})")

    if 0 < dropout <= 1:
        layers.append(nn.Dropout(dropout))
    return nn.Sequential(*layers)


def conv_block(c_in, c_out, kernel=3, stride=1, pad=1, pool_type='max', pool_kernel=2, pool_stride=2,
               batch_norm=False, activation='relu'):
    """
    available activation {relu, lrelu, sigmoid, tanh, elu, selu, softmax, lsoftmax}
    available pool_type {max, avg}
    """
    layers = [nn.Conv2d(c_in, c_out, kernel_size=kernel, stride=stride, padding=pad)]

    if batch_norm:
        layers.append(nn.BatchNorm2d(c_out))

    if activation in _act_func:
        layers.append(_act_func[activation])
    else:
        raise Exception(f"jcopdl supports ({', '.join(_act_func.keys())})")

    if pool_type == "max":
        layers.append(nn.MaxPool2d(pool_kernel, pool_stride))
    elif pool_type == "avg":
        layers.append(nn.AvgPool2d(pool_kernel, pool_stride))
    elif pool_type is None:
        pass
    else:
        raise Exception("jcopdl supports (max, avg)")
    return nn.Sequential(*layers)


def rnn_block(input_size, hidden_size, num_layers, cell_type, dropout=0, bidirectional=False):
    """
    available cell_type {rnn, lstm, gru}
    """
    params = {
        "input_size": input_size,
        "hidden_size": hidden_size,
        "num_layers": num_layers,
        "dropout": dropout,
        "bidirectional": bidirectional,
        "batch_first": True
    }

    if cell_type == "rnn":
        return nn.RNN(**params)
    elif cell_type == "lstm":
        return nn.LSTM(**params)
    elif cell_type == "gru":
        return nn.GRU(**params)
    else:
        raise Exception("jcopdl supports (rnn, lstm, gru)")
