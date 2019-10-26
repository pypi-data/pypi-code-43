from os.path import dirname
from os.path import join

from cffi import FFI

ffi = FFI()
ffi.cdef('''
void jenks_matrices(
    const int data_len, const int n_classes, double *data,
    unsigned int *lower_class_limits,
    double *variance_combinations);
''')

ffi.set_source(
    'jenks_natural_breaks._jenks_matrices',
    open(join(dirname(__file__), '_jenks_matrices.c')).read()
)

if __name__ == '__main__':
    ffi.compile()
