##########################################################################
# $Id: rpython.py 4480 2013-12-20 23:20:21Z boverhof $
# Dan Gunter <dkgunter@lbl.gov>
# See LICENSE.md for copyright notice!
#
#   $Author: boverhof $
#   $Date: 2013-12-20 15:20:21 -0800 (Fri, 20 Dec 2013) $
#   $Rev: 4480 $
#
# Provide a Python API for easy interfacing with R.
# Depends on RPy2: http://rpy.sourceforge.net/rpy2.html
#
###########################################################################
# System imports
import datetime
import gc
import time
# Third-party imports
# -- R --
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import rpy2.rlike.container as rlc

# Import R base
base = importr('base')
# Import NetLogger R package
#nlr = importr('netlogger')

R = robjects.r  # : Running R instance


class COLTYPE:
    """Enumeration of column types.
    """
    INT = 1  # : Python int
    FLOAT = 2  # : floats
    STR = 3  # : strings
    DATE = 4  # : float or datetime.datetime
    FACTOR = 5  # : strings
    BOOL = 6  # : bool

    # Empty values
    NONE = [None,
            0,  # INT
            0.0,  # FLOAT
            "",  # STR
            datetime.datetime(1970, 1, 1),  # DATE
            "",  # FACTOR
            True  # BOOL
            ]

    @staticmethod
    def from_value(value, factors=True):
        """Return an inferred column type.
        """
        if isinstance(value, int):
            return COLTYPE.INT
        if isinstance(value, float) or isinstance(value, long):
            return COLTYPE.FLOAT
        if isinstance(value, datetime.datetime):
            return COLTYPE.DATE
        if isinstance(value, bool):
            return COLTYPE.BOOL
        return (COLTYPE.STR, COLTYPE.FACTOR)[factors]


def get_coltypes(values):
    return map(COLTYPE.from_value, values)


def datetime_to_sec(dt):
    """Convert datetime object to number of seconds since 1/1/1970.

    Args:
      dt - Datetime object

    Return:
      Seconds (as a float) since the UNIX epoch.
    """
    return time.mktime(dt.timetuple()) + dt.microsecond/1e6


def make_data_frame(colnames, coltypes, rows=None, cols=None):
    """Make a data frame from a list of rows or columns and definitions
    (name and type) of the columns found in each row.

    See COLTYPE documentation for a description of accepted input types
    for each column type.

    Args:
      - rows (object[][]): Rows of data, each of the same length and types
      - cols (object[][]): Columns of data, each of the same length
      - colnames (str[]): Name of each column
      - column_type (COLTYPE[]): Type of each column. 

    Return:
      - robjects.DataFrame: Data frame

    Exceptions:
      - TypeError: Column value does not match stated type
    """
    # Check trivial cases.
    if (rows is not None and len(rows) == 0) or \
       (cols is not None and len(cols) == 0):
        return robjects.DataFrame({})
    # Transpose rows into appropriately typed columns.
    if rows is not None:
        columns = rlc.TaggedList([])
        for i in range(len(rows[0])):
            col = []
            for row in rows:
                col.append(row[i])
            # convert column to R type
            ct = coltypes[i]
            vec = make_rvector(col, ct)
            columns.append(vec, tag=colnames[i].encode())
    elif cols is not None:
        columns = rlc.TaggedList([])
        for (vec, ct, name) in zip(cols, coltypes, colnames):
            columns.append(make_rvector(vec, ct), tag=name.encode())
    else:
        raise ValueError("one of 'rows' or 'cols' must be given")
    # Create data frame from columns.
    df = robjects.DataFrame(columns)
    # Collect temporaries [perhaps]
    gc.collect()
    return(df)


def make_rvector(col, ct=COLTYPE.FLOAT):
    """Make and return an R vector for data in `col` of COLTYPE ct.

    Returns:
      robjects.Vector
    Raises:
      TypeError if the type is unknown
      TypeError if it is COLTYPE.DATE but not parseable
    """
    if ct == COLTYPE.INT:
        vec = robjects.IntVector(col)
    elif ct == COLTYPE.FLOAT:
        vec = robjects.FloatVector(col)
    elif ct == COLTYPE.STR:
        # Use I() from R.base library to avoid conversion
        # into a factor. Usually though a factor is what you want.
        vec = base.I(robjects.StrVector(col))
    elif ct == COLTYPE.BOOL:
        vec = robjects.BoolVector(col)
    elif ct == COLTYPE.FACTOR:
        # conversion will happen automatically
        vec = robjects.StrVector(col)
    elif ct == COLTYPE.DATE:
        field = col[0]
        if isinstance(field, datetime.datetime):
            tcol = map(datetime_to_sec, col)
        elif isinstance(field, float):
            tcol = col
        else:
            raise TypeError("Bad date type '%s' for column %d, '%s'. "
                            "Expected time.struct_time, "
                            "datetime.datetime, or float." % (
                                type(field), i, colnames[i]))
        vec = robjects.FloatVector(tcol)
    else:
        raise TypeError("Unknown type '%s' for column %d, '%s'." % (
            type(field), i, colnames[i]))
    return(vec)


def cursor_data_frame(cursor, column_types={}):
    """Iterate through cursor and return an R DataFrame object
    that represents its rows.

    It is assumed that all records have the same structure.
    If a record is missing any fields, it will be silently ignored.

    This is not a streaming algorithm. Temporary storage of 3x the
    original size is required. All records will be loaded
    into memory, then duplicated by make_data_frame(), and copied
    again by R into the DataFrame object itself.

    Args:
      - cursor (iterable): The 'cursor' is anything that supports the iterator
                 protocol. The expected datatype returned at each iteration is
                 a dictionary-like object that supports `keys()` and `get()`.
      - column_types (dict): Mapping of column names to values in COLTYPE

    Return:
      robject.DataFrame

    Exceptions:
      - StopIteration: If there is no data in the cursor.
    """
    table = []
    colnames, coltypes = [], []
    # Create table from iterated rows.
    first = True
    for row in cursor:
        if first:  # use this because .next() won't work on lists
            # Place column types in same order as 'colnames'
            for name in row.keys():
                coltypes.append(column_types.get(name,
                                                 COLTYPE.from_value(row[name])))
                colnames.append(name)
            first = False
        table_row, ignore = [], False
        for i, name in enumerate(colnames):
            try:
                value = row[name]
            except KeyError:
                value = COLTYPE.NONE[coltypes[i]]
            table_row.append(value)
        if not ignore:
            table.append(table_row)
    # Convert to R data frame
    df = make_data_frame(table, colnames, coltypes)
    return(df)
