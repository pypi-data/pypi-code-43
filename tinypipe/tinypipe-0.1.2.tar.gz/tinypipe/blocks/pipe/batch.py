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

import collections
import queue

from tinypipe.blocks.pipe import base as base_pipe


class BatchPipe(base_pipe.FetchRetryPipe):
  """Groups data into batches."""
  def __init__(self,
               batch_size,
               max_retry=None,
               fetch_time=None):
    super(BatchPipe, self).__init__(
        max_retry=max_retry, fetch_time=fetch_time)
    self._batch_size = batch_size
    self._batched = []

  def _run(self):
    try:
      data = self._fetch_data()
      self._batched.append(data)
    except queue.Empty:
      pass
    if ((len(self._batched) >= self._batch_size) or
        (self._batched and not self._running and
         self._retry_count >= self._max_retry // 2)):
      self._qout.put(list(self._batched))
      [self._qin.task_done() for _ in range(len(self._batched))]
      self._batched.clear()


class UnbatchPipe(base_pipe.FetchRetryPipe):
  """Unbatches data into individual elements."""
  def __init__(self, max_retry=None, fetch_time=None):
    super(UnbatchPipe, self).__init__(
        max_retry=max_retry, fetch_time=fetch_time)

  def _run(self):
    try:
      data = self._fetch_data()
      if isinstance(data, collections.Iterable):
        for element in data: self._qout.put(element)
      else:
        self._qout.put(data)
      self._qin.task_done()
    except queue.Empty:
      pass
