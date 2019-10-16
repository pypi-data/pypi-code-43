try:
   import h5py
except ImportError:
   no_h5py = True


def save_model(filepath):
    if no_h5py:
        raise ImportError('Missing Module: h5py not found')

    f = h5py.File(filepath = filepath, mode='w')

    try:

    finally:
        f.close()
