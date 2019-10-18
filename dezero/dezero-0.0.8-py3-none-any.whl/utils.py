import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


def _dot_var(v):
    dot_var = '{} [label="{}", color=orange, style=filled]\n'
    name = ''
    if hasattr(v, 'name') and v.name is not None:
        name = v.name

    return dot_var.format(id(v), name)


def _dot_func(f):
    # for function
    dot_func = '{} [label="{}", color=lightblue, style=filled, shape=box]\n'
    ret = dot_func.format(id(f), f.__class__.__name__)

    # for edge
    dot_edge = '{} -> {}\n'
    for x in f.inputs:
        ret += dot_edge.format(id(x), id(f))
    for y in f.outputs:
        ret += dot_edge.format(id(f), id(y))
    return ret


def get_dot_graph(y):
    funcs = []
    seen_set = set()

    def add_func(f):
        if f not in seen_set:
            funcs.append(f)
            # funcs.sort(key=lambda x: x.priority)
            seen_set.add(f)

    add_func(y.creator)
    txt = _dot_var(y)

    while funcs:
        func = funcs.pop()
        txt += _dot_func(func)
        for x in func.inputs:
            txt += _dot_var(x)

            if x.creator is not None:
                add_func(x.creator)

    return 'digraph g {\n' + txt + '}'





def axis2shape(input_shape, axis, keepdims=False):
    if axis == None:
        if keepdims == True:
            return np.ones(len(input_shape))
        else:
            return ()
    elif type(axis) == int:
        _shape = list(input_shape)
        if keepdims == False:
            _shape.pop(axis)
        else:
            _shape[axis] = 1
        return tuple(_shape)

    raise AssertionError("axis is `int` or `None` ( Not support for `tuple` )")


def sum_to(x, shape):
    ndim = len(shape)
    lead = x.ndim - ndim
    lead_axis = tuple(range(lead))

    axis = tuple([i + lead for i, sx in enumerate(shape) if sx == 1])
    y = x.sum(lead_axis + axis, keepdims=True)

    if lead > 0:
        y = y.squeeze(lead_axis)
    return y


def plot_surface(func, x0_arange=[-2.0, 2.0, 0.01], x1_arange=[-2.0, 2.0, 0.01]):
    xs = np.arange(*x0_arange)
    ys = np.arange(*x1_arange)

    X, Y = np.meshgrid(xs, ys)
    Z = func(X, Y)

    fig = plt.figure()
    ax = Axes3D(fig, azim=-128, elev=43)

    ax.set_xlabel("x0")
    ax.set_ylabel("x1")
    ax.set_zlabel("y")

    ax.plot_wireframe(X, Y, Z)
    #ax.contour(X, Y, Z, offset=1)#, colors="black", offset=-1)
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, norm=LogNorm(),
                    linewidth=0, edgecolor='none', cmap="viridis", alpha=0.8)
    plt.show()
    # plt.savefig("Rosenbrock1.svg", bbox_inches="tight")


def plot_grad(xlist):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    THRESHOUD_SCALE = 1.0
    max_scale = -1
    for xs in xlist:
        x0, x1 = xs
        scale = np.square(x0.grad **2 + x1.grad**2)
        if max_scale < scale:
            max_scale = scale
    grad_scale = THRESHOUD_SCALE / max_scale

    for xs in xlist:
        x0, x1 = xs

        start = (float(x0.data), float(x1.data))
        end = (float(x0.data + grad_scale * x0.grad),
               float(x1.data + grad_scale * x1.grad))
        print(start, end)
        ax.annotate('', xy=end, xytext=start,
                arrowprops=dict(shrink=0, width=1, headwidth=8,
                                headlength=10, connectionstyle='arc3',
                                facecolor='gray', edgecolor='gray')
                )


    ax.set_xlim([-5, 5])
    ax.set_ylim([-5, 5])

    plt.show()