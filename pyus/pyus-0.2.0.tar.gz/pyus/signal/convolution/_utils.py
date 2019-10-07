import numpy as np


def _flatten_array_as_2d(a: np.ndarray, axis: int) -> np.ndarray:
    # Create flattened 2D view (no copy)
    a_moveaxis = np.moveaxis(a=a, source=axis, destination=-1)
    _2d_view = a_moveaxis.reshape(-1, a_moveaxis.shape[-1])

    return _2d_view


def _broadcast_to_out_shape(
        inp: np.ndarray, out: np.ndarray, axis: int
) -> np.ndarray:
    # Broadcast array to output shape w.r.t. axis
    inp_len = inp.shape[axis]
    inp_bc_shape = list(out.shape)
    inp_bc_shape[axis] = inp_len
    inp_bc = np.broadcast_to(inp, shape=inp_bc_shape)
    return inp_bc
