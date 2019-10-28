# Copyright 2019 Siu-Kei Muk (David). All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import queue

from tinypipe.blocks.pipe import base as pipe_base


class FunctionPipe(pipe_base.FetchRetryPipe):
  """Simple function pipe.

  This `Pipe` performs a simple function call on each data and feeds the
  result into the output queue. A single-argument function must be provided.

  For example:

  ```python
  import tinypipe as tp

  def f(data):
    ...
    return result

  pipe = tp.pipe.FunctionPipe(f)

  pipeline = tp.Pipeline()
  pipeline.append(pipe)
  pipeline.start()
  ```
  """
  def __init__(self,
               fn,
               max_retry=None,
               fetch_time=None,
               drop_none=True):
    super(FunctionPipe, self).__init__(
        max_retry=max_retry, fetch_time=fetch_time)
    self._fn = fn
    self._drop_none = drop_none

  def _run(self):
    try:
      data = self._fetch_data()
      out = self._fn(data)
      if self._qout is not None and not (self._drop_none and out is None):
        self._qout.put(out)
      self._qin.task_done()
    except queue.Empty:
      pass
