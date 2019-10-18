# import pytest
from modelx.core.project import (
    write_model,
    read_model)
from modelx.testing import testutil
import modelx as mx
import os.path

m, s = mx.new_model(), mx.new_space()

s.new_cells("foo")

s.foo = "foo"
