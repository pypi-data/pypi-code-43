import numpy as np
import dezero
from dezero.core import Function, Variable, as_variable
from dezero import cuda
from dezero import utils


# =========================================================
# sin / cos / tanh / exp / log
# ========================================================
class Sin(Function):
    def forward(self, x):
        xp = cuda.get_array_module(x)
        y = xp.sin(x)
        return y

    def backward(self, gy):
        x, = self.inputs
        gx = gy * cos(x)
        return gx


def sin(x):
    f = Sin()
    return f(x)


class Cos(Function):
    def forward(self, x):
        xp = cuda.get_array_module(x)
        y = xp.cos(x)
        return y

    def backward(self, gy):
        x, = self.inputs
        gx = gy * -sin(x)
        return gx


def cos(x):
    f = Cos()
    return f(x)


class Tanh(Function):
    def forward(self, x):
        xp = cuda.get_array_module(x)
        return xp.tanh(x)

    def backward(self, gy):
        y, = self.outputs
        gx = gy * (1 - y * y)
        return gx


def tanh(x):
    f = Tanh()
    return f(x)


class Exp(Function):
    def forward(self, x):
        xp = cuda.get_array_module(x)
        return xp.exp(x)

    def backward(self, gy):
        y, = self.outputs
        gx = gy * y
        return gx


def exp(x):
    f = Exp()
    return f(x)


class Log(Function):
    def forward(self, x):
        xp = cuda.get_array_module(x)
        return xp.log(x)

    def backward(self, gy):
        x, = self.inputs
        gx = gy / x
        return gx


def log(x):
    f = Log()
    return f(x)


# ==========================================================
# for Tensor: sum / repeat / reshape / sum_to / broadcast_to
# ==========================================================

class Reshape(Function):
    def __init__(self, shape):
        self.shape = shape

    def forward(self, x):
        return x.reshape(self.shape)

    def backward(self, gy):
        x, = self.inputs
        return reshape(gy, x.shape)


def reshape(x, shape):
    f = Reshape(shape)
    return f(x)


def expand_dims(x, axis):
    shape = list(x.shape)
    shape.insert(axis, 1)
    return reshape(x, tuple(shape))


class Sum(Function):
    def __init__(self, axis):
        """
        引数のaxisはintのみ
        """
        self.axis = axis

    def forward(self, x):
        y = x.sum(self.axis)
        return y

    def backward(self, gy):
        x, = self.inputs
        repeats = x.shape[self.axis]
        gx = expand(gy, repeats, self.axis)
        return gx


def sum(x, axis=None):
    if axis is None:
        for _ in range(x.ndim):
            x = sum(x, 0)
        return x
    else:
        f = Sum(axis)
        return f(x)


class Expand(Function):
    def __init__(self, repeats, axis):
        """
        引数のaxisはintのみ
        """
        self.repeats = repeats
        self.axis = axis

    def forward(self, x):
        xp = dezero.cuda.get_array_module(x)
        y = xp.expand_dims(x, self.axis)
        y = xp.repeat(y, self.repeats, self.axis)
        return y

    def backward(self, gy):
        gx = sum(gy, self.axis)
        return gx


def expand(x, repeats, axis):
    f = Expand(repeats, axis)
    return f(x)


class SumTo(Function):
    def __init__(self, shape):
        self.shape = shape

    def forward(self, x):
        if x.shape == self.shape:
            return x

        y = utils.sum_to(x, self.shape)
        return y

    def backward(self, gy):
        x, = self.inputs
        gx = broadcast_to(gy, x.shape)
        return gx


def sum_to(x, shape):
    f = SumTo(shape)
    return f(x)


class BroadcastTo(Function):
    def __init__(self, shape):
        self.shape = shape

    def forward(self, x):
        xp = dezero.cuda.get_array_module(x)
        y = xp.broadcast_to(x, self.shape)
        return y

    def backward(self, gy):
        x, = self.inputs
        gx = sum_to(gy, x.shape)
        return gx


def broadcast_to(x, shape):
    if x.shape == shape:
        return x

    f = BroadcastTo(shape)
    return f(x)


class MatMul(Function):
    def forward(self, x, W):
        y = x.dot(W)
        return y

    def backward(self, gy):
        x, W = self.inputs
        gx = matmul(gy, transpose(W))
        gW = matmul(transpose(x), gy)
        return gx, gW


def matmul(x, W):
    f = MatMul()
    return f(x, W)


class Transpose(Function):
    def forward(self, x):
        assert x.ndim <= 2  # 3次元以上の配列は非対応
        y = np.transpose(x)
        return y

    def backward(self, gy):
        gx = transpose(gy)
        return gx


def transpose(x):
    f = Transpose()
    return f(x)


# ==========================================================
# activation / loss function
# ==========================================================

def mean_squared_error(y1, y2):
    y1, y2 = as_variable(y1), as_variable(y2)

    N = y1.shape[0]
    diff = y1 - y2
    loss = sum(diff * diff) / N
    return loss


def sigmoid(x):
    x = as_variable(x)
    y = 1 / (1 + exp(-x))
    return y


class ReLU(Function):
    def forward(self, x):
        xp = cuda.get_array_module(x)
        y = xp.maximum(x, 0.0)
        return y

    def backward(self, gy):
        x, = self.inputs
        mask = x.data > 0
        gx = gy * mask
        return gx


def relu(x):
    f = ReLU()
    return f(x)


def softmax(x, axis=1):
    x = as_variable(x)
    y = exp(x)
    sum_shape = list(y.shape)
    sum_shape[axis] = 1
    sum_y = sum_to(y, sum_shape)

    return y / sum_y


def softmax_cross_entropy(x, t):
    x, t = as_variable(x), as_variable(t)
    N = x.shape[0]

    p = softmax(x)
    log_p = log(p)
    tlog_p = log_p[np.arange(N), t.data]
    y = -1 * sum(tlog_p) / N
    return y


def accuracy(y, t):
    """
    [WAR] this functions is not differentiable
    """
    y, t = as_variable(y), as_variable(t)

    pred = y.data.argmax(axis=1).reshape(t.shape)
    result = (pred == t.data)
    acc = result.mean()
    return Variable(acc)


class GetItem(Function):
    def __init__(self, slices):
        self.slices = slices

    def forward(self, x):
        return x[self.slices]

    def backward(self, gy):
        x, = self.inputs
        return GetItemGrad(self.slices, x.shape)(gy)


class GetItemGrad(Function):
    def __init__(self, slices, in_shape):
        self.slices = slices
        self.in_shape = in_shape

    def forward(self, gy):
        xp = dezero.cuda.get_array_module(gy)
        gx = xp.zeros(self.in_shape)

        if xp is np:
            np.add.at(gx, self.slices, gy)
        else:
            xp.scatter_add(gx, self.slices, gy)
        return gx

    def backward(self, ggx):
        return get_item(ggx, self.slices)


def get_item(x, slices):
    f = GetItem(slices)
    return f(x)


def embed_id(x, W):
    return W[x]


class Max(Function):
    def __init__(self, axis=None, keepdims=False):
        self.axis = axis
        self.keepdims = keepdims

    def forward(self, x):
        return x.max(x, axis=self.axis, keepdims=self.keepdims)

    def backward(self, gy):
        x = self.inputs[0]
        y = self.outputs[0]

        if self.axis is None:
            axis = range(x.ndim)
        elif isinstance(self.axis, int):
            axis = (self.axis,)
        else:
            axis = self.axis

        # Add broadcastable dimensions to y and gy
        # for each one that was reduced in the forward operation
        shape = [s if ax not in axis else 1 for ax, s in enumerate(x.shape)]
        #gy = gy.reshape(shape)
        #y = y.reshape(shape)
        gy = reshape(gy, shape)
        y = reshape(y, shape)
        cond = (x.data == y.data)
        gy = broadcast_to(gy, cond.shape)
        return gy * cond


class Min(Max):
    def forward(self, x):
        return x.min(axis=self.axis, keepdims=self.keepdims)


def max(x, axis=None, keepdims=False):
    f = Max(axis, keepdims)
    return f(x)


def min(x, axis=None, keepdims=False):
    f = Min(axis, keepdims)
    return f(x)



add = dezero.core.add
sub = dezero.core.sub
rsub = dezero.core.rsub
mul = dezero.core.mul
div = dezero.core.div
neg = dezero.core.neg
pow = dezero.core.pow