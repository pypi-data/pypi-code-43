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

from tinypipe.blocks import base_block
from tinypipe.utils import general as gen_utils


class Pipe(base_block.Block):
  """Operation unit of pipeline.

  A Pipe acts as a function that takes inputs from its input queue. Results
  are fed to the output queue (if present). Each Pipe operates in its own
  thread, so every unit runs in parallel in the pipeline.

  Descendants are required to implement the following methods:

  - `_run`: This is where the operation logic lives. It should do the following:

      1. Fetch data from input queue.
      2. Process data
      3. Feed result into output queue (if present).

  - `_ready_to_terminate`: Indicates whether the Pipe is ready to terminate.
      Typically, this checks if all input data is processed.

  A Pipe must be built through `build(qin, qout)` before running, where
  `qin` and `qout` are `queue.Queue` instances. `qin` is the input queue from
  which the operation fetches data, and `qout` is the output queue to which
  the results are fed. While `qin` is required, `qout` is optional. If `qout` is
  not provided, it is interpreted that outputs are not required.

  The Pipe will keep running until `wrap_up()` is called, which signals the
  pipe to shutdown after completing processing the remaining inputs.
  """
  def __init__(self):
    super(Pipe, self).__init__()
    self._qin = None
    self._qout = None

  def _build_pipe(self):
    pass

  def _build(self, qin: queue.Queue, qout: queue.Queue=None):
    # TODO: Validate inputs
    self._qin = qin
    self._qout = qout
    self._build_pipe()

  def wrap_up(self):
    super(Pipe, self).wrap_up()
    self.join()


class FetchRetryPipe(Pipe):
  def __init__(self,
               max_retry=None,
               fetch_time=None):
    super(FetchRetryPipe, self).__init__()
    self._max_retry = gen_utils.val_or_default(max_retry, 10)
    self._fetch_time = gen_utils.val_or_default(fetch_time, 0.01)
    self._retry_count = 0

  def _fetch_data(self):
    try:
      data = self._qin.get(timeout=self._fetch_time)
      self._retry_count = 0
      return data
    except queue.Empty:
      if not self._running:
        self._retry_count += 1
      raise

  def _ready_to_terminate(self):
    return self._retry_count >= self._max_retry
