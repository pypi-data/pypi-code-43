import contextlib
import numpy as np
import dezero.functions as F
from dezero.core import Variable, Parameter


class Layer:
    def __init__(self):
        self._params = set()

    def __setattr__(self, name, value):
        if isinstance(value, (Parameter, Layer)):
            self._params.add(value)
        super().__setattr__(name, value)

    def params(self):
        for obj in self._params:
            if isinstance(obj, Layer):
                yield from obj.params()
            else:
                yield obj

    def cleargrads(self):
        for param in self.params():
            param.cleargrad()

    def to_cpu(self):
        for param in self.params():
            param.to_cpu()

    def to_gpu(self):
        for param in self.params():
            param.to_gpu()

    def serialize(self, serializer):
        d = self.__dict__
        for name, value in d.items():
            if isinstance(value, Variable):
                serializer(name, value.data)

# alias
Model = Layer


class Linear(Layer):
    def __init__(self, in_size, out_size, nobias=False):
        super().__init__()

        I, O = in_size, out_size
        self.W = Parameter(np.random.randn(I, O) * np.sqrt(1/I), name='W')
        if nobias:
            self.b = None
        else:
            self.b = Parameter(np.zeros(O), name='b')

    def __call__(self, x):
        y = F.matmul(x, self.W)
        if self.b is not None:
            y += self.b
        return y


class EmbedID(Layer):
    def __init__(self, in_size, out_size):
        super().__init__()
        self.W = Parameter(np.random.randn(in_size, out_size), name='W')

    def __call__(self, x):
        y = self.W[x]
        return y


class RNN(Layer):
    def __init__(self, in_size, hidden_size):
        super().__init__()
        I, H = in_size, hidden_size
        self.x2h = Linear(I, H)
        self.h2h = Linear(H, H)
        self.h = None

    def reset_state(self):
        self.h = None

    def __call__(self, x):
        if self.h is None:
            h_new = F.tanh(self.x2h(x))
        else:
            h_new = F.tanh(self.x2h(x) + self.h2h(self.h))

        self.h = h_new
        return h_new


class LSTM(Layer):
    def __init__(self, in_size, hidden_size):
        super().__init__()

        I, H = in_size, hidden_size
        self.x2f = Linear(I, H)
        self.x2i = Linear(I, H)
        self.x2o = Linear(I, H)
        self.x2u = Linear(I, H)
        self.h2f = Linear(H, H, nobias=True)
        self.h2i = Linear(H, H, nobias=True)
        self.h2o = Linear(H, H, nobias=True)
        self.h2u = Linear(H, H, nobias=True)

        self.reset_state()

    def reset_state(self):
        self.h = None
        self.c = None

    def __call__(self, x):
        if self.h is None:
            N, D = x.shape
            H, H = self.h2f.W.shape
            self.h = np.zeros((N, H), np.float32)
            self.c = np.zeros((N, H), np.float32)

        f = F.sigmoid(self.x2f(x) + self.h2f(self.h))
        i = F.sigmoid(self.x2i(x) + self.h2i(self.h))
        o = F.sigmoid(self.x2o(x) + self.h2o(self.h))
        u = F.tanh(self.x2u(x) + self.h2u(self.h))

        c = (f * self.c) + (i * u)
        h = o * F.tanh(c)

        self.h, self.c = h, c
        return h


class LSTM2(Layer):
    def __init__(self, in_size, hidden_size):
        super().__init__()

        I, H = in_size, hidden_size

        self.x2d = Linear(I, 4*H)
        self.h2d = Linear(H, 4*H)

        self.reset_state()

    def reset_state(self):
        self.h = None
        self.c = None

    def __call__(self, x):
        H = self.h2d.W.shape[0]
        if self.h is None:
            N, D = x.shape
            self.h = np.zeros((N, H), np.float32)
            self.c = np.zeros((N, H), np.float32)
        d = self.x2d(x) + self.h2d(self.h)

        f = F.sigmoid(d[:,:H])
        i = F.sigmoid(d[:,H:2*H])
        o = F.sigmoid(d[:,2*H:3*H])
        u = F.tanh(d[:,3*H:])

        c = (f * self.c) + (i * u)
        h = o * F.tanh(c)

        self.h, self.c = h, c
        return h