import sys

from psutil   import virtual_memory
from tempfile import gettempdir

from numpy.ma import masked as numpy_ma_masked
from numpy.ma import nomask as numpy_ma_nomask

from . import mpi_on
from . import mpi_size

#platform = sys.platform
#if platform == 'darwin':
#    from psutil import virtual_memory

# --------------------------------------------------------------------
# Find the total amount of memory, in bytes
# --------------------------------------------------------------------
_TOTAL_MEMORY = float(virtual_memory().total)
#if platform == 'darwin':
#    # MacOS
#    _MemTotal = float(virtual_memory().total)
#else:
#    # Linux
#    _meminfo_file = open('/proc/meminfo', 'r', 1)
#    for line in _meminfo_file:
#        field_size = line.split()
#        if field_size[0] == 'MemTotal:':
#            _MemTotal = float(field_size[1]) * 1024
#            break
#    #--- End: for
#    _meminfo_file.close()
##--- End: if



# --------------------------------------------------------------------
#   A dictionary of useful constants.
#
#   Whilst the dictionary may be modified directly, it is safer to
#   retrieve and set the values with a function where one is
#   provided. This is due to interdependencies between some values.
#
#   :Keys:
#
#        ATOL : float
#	    The value of absolute tolerance for testing numerically
#	    tolerant equality.
#
#        TOTAL_MEMORY : float
#	    Find the total amount of physical memory (in bytes).
#
#        CHUNKSIZE : float
#	    The chunk size (in bytes) for data storage and
#	    processing.
#
#        FM_THRESHOLD : float
#	    The minimum amount of memory (in bytes) to be kept free
#	    for temporary work space. This should always be
#	    MINNCFM*CHUNKSIZE.
#
#        MINNCFM : int
#	    The number of chunk sizes to be kept free for temporary
#	    work space.
#
#        OF_FRACTION : float
#	    The fraction of the maximum number of concurrently open
#	    files which may be used for files containing data
#	    arrays.
#
#        RTOL : float
#	    The value of relative tolerance for testing numerically
#	    tolerant equality.
#
#        TEMPDIR : str
#	    The location to store temporary files. By default it is
#	    the default directory used by the :mod:`tempfile` module.
#
#        REGRID_LOGGING : bool
#           Whether or not to enable ESMPy logging. If it is logging
#           is performed after every call to ESMPy. By default logging
#           is disabled.
#
#        FREE_MEMORY_FACTOR : int
#           Factor to divide the free memory by. If MPI is on this is
#           equal to the number of PEs. Otherwise it is equal to 1 and
#           is ignored in any case.
#
#        COLLAPSE_PARALLEL_MODE : int
#           The mode to use when parallelising collapse. By default
#           this is 0 to try and automatically determine which mode to
#           use.
#
# --------------------------------------------------------------------
CONSTANTS = {'RTOL'                  : sys.float_info.epsilon,
             'ATOL'                  : sys.float_info.epsilon,
             'TEMPDIR'               : gettempdir(),
             'OF_FRACTION'           : 0.5,
             'TOTAL_MEMORY'          : _TOTAL_MEMORY,
             'FREE_MEMORY_FACTOR'    : 0.1,
             'WORKSPACE_FACTOR_1'    : 2.0,
             'WORKSPACE_FACTOR_2'    : 8.0,
             'REGRID_LOGGING'        : False,
             'COLLAPSE_PARALLEL_MODE': 0,
             'RELAXED_IDENTITIES'    : False,
             'IGNORE_IDENTITIES'     : False,
             }

CONSTANTS['FM_THRESHOLD'] = CONSTANTS['FREE_MEMORY_FACTOR'] * CONSTANTS['TOTAL_MEMORY']

CONSTANTS['CHUNKSIZE'] = (CONSTANTS['FM_THRESHOLD'] /
                          (mpi_size * CONSTANTS['WORKSPACE_FACTOR_1'] + CONSTANTS['WORKSPACE_FACTOR_2']))

masked = numpy_ma_masked
nomask = numpy_ma_nomask

_file_to_fh = {}

