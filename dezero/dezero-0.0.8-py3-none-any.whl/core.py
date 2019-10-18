import numpy as np
import contextlib
import dezero

# =========================================================
# ======================= Config ==========================
# =========================================================
class Config:
    enable_backprop = True

config = Config()


@contextlib.contextmanager
def using_config(name, value):
    old_value = getattr(config, name)
    setattr(config, name, value)
    yield
    setattr(config, name, old_value)


def no_grad():
    return using_config('enable_backprop', False)


# =========================================================
# ================= Variable / Function ===================
# =========================================================
class Variable:

    __array_priority__ = 200

    def __init__(self, data, name=None):
        self.data = data
        self.name = name
        self.grad = None
        self.creator = None
        self.priority = 0

    @property
    def shape(self):
        return self.data.shape

    @property
    def ndim(self):
        return self.data.ndim

    @property
    def size(self):
        return self.data.size

    @property
    def dtype(self):
        return self.data.dtype

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        #return '%s(%s)' % ('variable', np.array2string(self.data))
        #return repr(self.data)
        p = str(self.data).replace('\n', '\n' + ' ' * 9)
        return 'variable(' + p + ')'
        #return 'variable(%s)' % (repr(self.data))

    def set_creator(self, func):
        self.creator = func
        self.priority = func.priority + 1

    def unchain(self):
        self.creator = None

    def cleargrad(self):
        self.grad = None

    def backward(self, retain_grad=False, create_graph=False):
        if self.grad is None:
            xp = dezero.cuda.get_array_module(self.data)
            self.grad = Variable(xp.ones_like(self.data))

        funcs = []
        seen_set = set()

        def add_func(f):
            if f not in seen_set:
                funcs.append(f)
                seen_set.add(f)
                funcs.sort(key=lambda x: x.priority)

        add_func(self.creator)
        while funcs:
            f = funcs.pop()
            gys = [output.grad for output in f.outputs]

            with using_config('enable_backprop', create_graph):
                gxs = f.backward(*gys)
            if not isinstance(gxs, tuple):
                gxs = (gxs,)

            for x, gx in zip(f.inputs, gxs):
                if x.grad is None:
                    x.grad = gx
                else:
                    x.grad = x.grad + gx

                if x.creator is not None:
                    add_func(x.creator)

            if not retain_grad:
                for y in f.outputs:
                    y.cleargrad()

    def unchain_backward(self):
        funcs = []
        seen_set = set()

        def add_func(f):
            if f not in seen_set:
                funcs.append(f)
                seen_set.add(f)

        add_func(self.creator)
        self.unchain()

        while funcs:
            func = funcs.pop()
            for x in func.inputs:

                if x.creator is not None:
                    add_func(x.creator)
                    x.unchain()

    def to_cpu(self):
        self.data = dezero.cuda.as_numpy(self.data)

    def to_gpu(self):
        self.data = dezero.cuda.as_cupy(self.data)


class Parameter(Variable):
    pass


class Function:
    def __call__(self, *inputs):
        inputs = [as_variable(x) for x in inputs]

        xs = [x.data for x in inputs]
        ys = self.forward(*xs)
        if not isinstance(ys, tuple):
            ys = (ys,)
        outputs = [Variable(y) for y in ys]

        if config.enable_backprop:
            self.priority = max([x.priority for x in inputs])
            for output in outputs:
                output.set_creator(self)
            self.inputs = inputs
            self.outputs = outputs

        return outputs if len(outputs) > 1 else outputs[0]

    def forward(self, xs):
        raise NotImplementedError()

    def backward(self, gys):
        raise NotImplementedError()


def as_variable(obj):
    if isinstance(obj, Variable):
        return obj
    return Variable(obj)


# =========================================================
# ============= 四則演算 / 演算子のオーバーロード =============
# =========================================================
def _broadcast_backward(gx0, gx1, x0, x1):
    if x0.shape == x1.shape:
        return gx0, gx1

    gx0 = dezero.functions.sum_to(gx0, x0.shape)
    gx1 = dezero.functions.sum_to(gx1, x1.shape)
    return gx0, gx1


class Add(Function):
    def forward(self, x0, x1):
        y = x0 + x1
        return y

    def backward(self, gy):
        gx0, gx1 = gy, gy

        x0, x1 = self.inputs
        gx0, gx1 = _broadcast_backward(gx0, gx1, x0, x1)
        return gx0, gx1


def add(x0, x1):
    if np.isscalar(x1):
        xp = dezero.cuda.get_array_module(x0.data)
        x1 = xp.array(x1)
    f = Add()
    y = f(x0, x1)
    return y


class Mul(Function):
    def forward(self, x0, x1):
        y = x0 * x1
        return y

    def backward(self, gy):
        x0, x1 = self.inputs
        gx0 = gy * x1
        gx1 = gy * x0

        x0, x1 = self.inputs
        gx0, gx1 = _broadcast_backward(gx0, gx1, x0, x1)
        return gx0, gx1


def mul(x0, x1):
    if np.isscalar(x1):
        xp = dezero.cuda.get_array_module(x0.data)
        x1 = xp.array(x1)
    f = Mul()
    return f(x0, x1)


class Neg(Function):
    def forward(self, x):
        return -x

    def backward(self, gy):
        return -gy


def neg(x):
    f = Neg()
    return f(x)


class Sub(Function):
    def forward(self, x0, x1):
        y = x0 - x1
        return y

    def backward(self, gy):
        gx0 = gy
        gx1 = gy * -1

        x0, x1 = self.inputs
        gx0, gx1 = _broadcast_backward(gx0, gx1, x0, x1)
        return gx0, gx1


def sub(x0, x1):
    if np.isscalar(x1):
        xp = dezero.cuda.get_array_module(x0.data)
        x1 = xp.array(x1)
    f = Sub()
    return f(x0, x1)


def rsub(x0, x1):
    if np.isscalar(x1):
        xp = dezero.cuda.get_array_module(x0.data)
        x1 = xp.array(x1)
    return sub(x1, x0)


class Div(Function):
    def forward(self, x0, x1):
        y = x0 / x1
        return y

    def backward(self, gy):
        x0, x1 = self.inputs
        gx0 = gy / x1
        gx1 = gy * (-x0 / x1**2)

        gx0, gx1 = _broadcast_backward(gx0, gx1, x0, x1)
        return gx0, gx1


def div(x0, x1):
    if np.isscalar(x1):
        xp = dezero.cuda.get_array_module(x0.data)
        x1 = xp.array(x1)
    f = Div()
    return f(x0, x1)


def rdiv(x0, x1):
    if np.isscalar(x1):
        xp = dezero.cuda.get_array_module(x0.data)
        x1 = xp.array(x1)
    return div(x1, x0)


class Pow(Function):
    def __init__(self, c):
        self.c = c

    def forward(self, x):
        try:
            y = x ** self.c
        except RuntimeWarning:
            print("とまった", x.shape, x, self.c)

        return y

    def backward(self, gy):
        x, = self.inputs
        c = self.c

        gx = c * x ** (c-1) * gy
        return gx


def pow(x, c):
    f = Pow(c)
    return f(x)



def setup_variable():
    Variable.__add__ = add
    Variable.__radd__ = add
    Variable.__mul__ = mul
    Variable.__rmul__ = mul
    Variable.__neg__ = neg
    Variable.__sub__ = sub
    Variable.__rsub__ = rsub
    Variable.__truediv__ = div
    Variable.__rtruediv__ = rdiv
    Variable.__pow__ = pow
    Variable.__getitem__ = dezero.functions.get_item

    Variable.sum = dezero.functions.sum
    Variable.matmaul = dezero.functions.matmul
    Variable.dot = dezero.functions.matmul
    Variable.transpose = dezero.functions.transpose
    Variable.reshape = dezero.functions.reshape
    Variable.max = dezero.functions.max
    Variable.min = dezero.functions.min