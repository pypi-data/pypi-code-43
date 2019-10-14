"""Includes all SQLAlchemy data-types, plus additional type specifiers:

* :class:`NumpyArray` - for storing Numpy arrays as *BLOB*\s
"""

import io
import numpy
from sqlalchemy.types import *


# TODO: Write a trivial test for this type specifier.
# TODO: This can be made more sophisticated by allowing to serialize as JSON, or by prefixing the dtype description to
#       bytes in C order.
class NumpyArray(TypeDecorator):
    impl = BLOB

    def process_bind_param(self, array, dialect):
        buffer = io.BytesIO()
        numpy.save(buffer, array, allow_pickle=False)
        buffer.seek(0)
        content = buffer.read()
        return content

    def process_result_value(self, value, dialect):
        buffer = io.BytesIO(value)
        array = numpy.load(buffer, allow_pickle=False)
        return array
