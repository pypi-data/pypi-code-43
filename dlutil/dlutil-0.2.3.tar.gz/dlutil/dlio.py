import numpy as np
import h5py
import torch
import torch.utils.data as Data

__all__ = ['write_h5_from_arrays',
           'write_h5_from_generator', 'H5Dataset', 'read_h5']


def _shape_check(a, with_batch=True):
    if with_batch:
        shape_dim_limit = 1
    else:
        shape_dim_limit = 0
    if len(a.shape) < shape_dim_limit:
        raise ValueError(f'Check {a.shape}')
    elif len(a.shape) == shape_dim_limit:
        a = a[..., np.newaxis]
    else:
        a = a
    return a

# Write data to HDF5


def write_h5_from_arrays(filename, xs, ys, is_appending=False):
    '''This function is to write h5 file using np arrays.
    xs: list of np arrays, which stands for x;
    ys: list of np arrays, which stands for y. (ys can be None for unsupervised learning)
    Caution: the length of x and y should be the same.
    '''
    if is_appending:
        fh5 = h5py.File(filename, mode='r+')
        h5xs = fh5['x']
        x_len = h5xs.attrs['len']
        xs_names = list(h5xs.keys())
        cur_len_x = len(xs[0])
        for name, x in zip(xs_names, xs):
            xds = h5xs[name]
            xds.resize((x_len+cur_len_x, *xds.shape[1:]))
            x = _shape_check(x, with_batch=True)
            xds[x_len:x_len+cur_len_x, ...] = x
        h5xs.attrs['len'] = x_len + cur_len_x
        if ys is not None:
            h5ys = fh5['y']
            y_len = h5ys.attrs['len']
            ys_names = list(h5ys.keys())
            cur_len_y = len(ys[0])
            for name, y in zip(ys_names, ys):
                yds = h5ys[name]
                yds.resize((y_len+cur_len_y, *yds.shape[1:]))
                y = _shape_check(y, with_batch=True)
                yds[y_len:y_len+cur_len_y, ...] = y
            h5ys.attrs['len'] = y_len + cur_len_y
            assert h5xs.attrs['len'] == h5ys.attrs['len'], 'length of x and y is inconsistent'
    else:
        fh5 = h5py.File(filename, mode='w')
        h5xs = fh5.create_group('x')
        cur_len_x = len(xs[0])
        h5xs.attrs['len'] = cur_len_x
        for i, x in enumerate(xs, start=1):
            x = _shape_check(x, with_batch=True)
            h5xs.create_dataset(
                f'x{i}', shape=x.shape, dtype=x.dtype, data=x, maxshape=(None, *x.shape[1:]))
        if ys is not None:
            h5ys = fh5.create_group('y')
            cur_len_y = len(ys[0])
            h5ys.attrs['len'] = cur_len_y
            for i, y in enumerate(ys, start=1):
                y = _shape_check(y, with_batch=True)
                h5ys.create_dataset(
                    f'y{i}', shape=y.shape, dtype=y.dtype, data=y, maxshape=(None, *y.shape[1:]))
            assert h5xs.attrs['len'] == h5ys.attrs['len'], 'length of x and y is inconsistent'
    fh5.close()


def write_h5_from_generator(filename, xgns, ygns, is_appending=False, preallocated_slots=5000):
    '''This function is to write h5 file using generators.
    xgns: list of generators, which stands for x;
    ygns: list of generators, which stands for y. (ygns can be None for unsupervised learning)
    Caution: data from generators has no batch dim, e.g. 32x32 RGB images will be generated using (3, 32, 32), not (batch, 3, 32, 32). Batch dim will be automatically added in hdf5 file.
    '''
    if is_appending:
        fh5 = h5py.File(filename, mode='r+')
        h5xs = fh5['x']
        x_len = h5xs.attrs['len']
        xs_names = list(h5xs.keys())
        for name, xgn in zip(xs_names, xgns):
            xds = h5xs[name]
            cur_len = 0
            for x in xgn:
                x = _shape_check(x, with_batch=False)
                if x_len + cur_len >= len(xds):
                    xds.resize((len(xds) + preallocated_slots, *xds.shape[1:]))
                xds[x_len+cur_len] = x
                cur_len += 1
            h5xs.attrs['len'] = x_len + cur_len
            xds.resize((x_len + cur_len, *xds.shape[1:]))
        if ygns is not None:
            h5ys = fh5['y']
            y_len = h5ys.attrs['len']
            ys_names = list(h5ys.keys())
            for name, ygn in zip(ys_names, ygns):
                yds = h5ys[name]
                cur_len = 0
                for y in ygn:
                    y = _shape_check(y, with_batch=False)
                    if y_len + cur_len >= len(yds):
                        yds.resize(
                            (len(yds) + preallocated_slots, *yds.shape[1:]))
                    yds[y_len+cur_len] = y
                    cur_len += 1
                h5ys.attrs['len'] = y_len + cur_len
                yds.resize((y_len + cur_len, *yds.shape[1:]))
            assert h5xs.attrs['len'] == h5ys.attrs['len'], 'length of x and y is inconsistent'
    else:
        fh5 = h5py.File(filename, mode='w')
        h5xs = fh5.create_group('x')
        for i, xgn in enumerate(xgns, start=1):
            x = next(xgn)
            x = _shape_check(x, with_batch=False)
            cur_len = 0
            xds = h5xs.create_dataset(f'x{i}', shape=(
                preallocated_slots, *x.shape), dtype=x.dtype, maxshape=(None, *x.shape))
            while True:
                try:
                    if cur_len >= len(xds):
                        xds.resize(
                            (len(xds) + preallocated_slots, *xds.shape[1:]))
                    xds[cur_len] = x
                    cur_len += 1
                    x = next(xgn)
                    x = _shape_check(x, with_batch=False)
                except StopIteration:
                    break
            h5xs.attrs['len'] = cur_len
            xds.resize((cur_len, *xds.shape[1:]))
        if ygns is not None:
            h5ys = fh5.create_group('y')
            for i, ygn in enumerate(ygns, start=1):
                y = next(ygn)
                y = _shape_check(y, with_batch=False)
                cur_len = 0
                yds = h5ys.create_dataset(f'y{i}', shape=(
                    preallocated_slots, *y.shape), dtype=y.dtype, maxshape=(None, *y.shape))
                while True:
                    try:
                        if cur_len >= len(yds):
                            yds.resize(
                                (len(yds) + preallocated_slots, *yds.shape[1:]))
                        yds[cur_len] = y
                        cur_len += 1
                        y = next(ygn)
                        y = _shape_check(y, with_batch=False)
                    except StopIteration:
                        break
                h5ys.attrs['len'] = cur_len
                yds.resize((cur_len, *yds.shape[1:]))
            assert h5xs.attrs['len'] == h5ys.attrs['len'], 'length of x and y is inconsistent'
    fh5.close()


# Read data from HDF5
class H5Dataset(Data.Dataset):
    def __init__(self, filename, transform_func=None):
        self.h5set = h5py.File(filename, mode='r')
        assert 'x' in self.h5set, 'key x is required'
        h5xs = self.h5set['x']
        self.x_len = h5xs.attrs['len']
        self.xs_names = list(h5xs.keys())
        self.xs = [h5xs[name] for name in self.xs_names]
        self.has_y = False
        self.transform_func = transform_func
        if 'y' in self.h5set:
            self.has_y = True
            h5ys = self.h5set['y']
            self.y_len = h5ys.attrs['len']
            assert self.x_len == self.y_len, 'data length inconsistent!'
            self.ys_names = list(h5ys.keys())
            self.ys = [h5ys[name] for name in self.ys_names]

    def __len__(self):
        return self.x_len

    def __getitem__(self, index):
        batch_xs = tuple((x[index] for x in self.xs))
        if self.has_y:
            batch_ys = tuple((y[index] for y in self.ys))
            if self.transform_func is None:
                return (batch_xs, batch_ys)
            return self.transform_func(batch_xs, batch_ys)
        else:
            if self.transform_func is None:
                return batch_xs
            return self.transform_func(batch_xs)

    def close(self):
        self.h5set.close()


def read_h5(filename, batch_size, shuffle=True, transform_func=None):
    h5dataset = H5Dataset(filename, transform_func=transform_func)
    steps_per_epoch = int(np.ceil(len(h5dataset) / batch_size))
    dataset_loader = Data.DataLoader(
        h5dataset, batch_size=batch_size, shuffle=shuffle)
    return dataset_loader, steps_per_epoch
