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

import logging
import queue
import threading
from typing import List

from tinypipe.blocks import pipe as pipe_lib


class Pipeline(object):
  """`Pipeline` groups a series of pipes into an object with

  Usage of `Pipeline` involves the following stages:
    1. Construct `Pipeline` by defining the responsible `Pipe` and append them
       to the pipeline in order.
    2. (Optional) Build the `Pipeline` with `pipeline.build()`.
    3. Start the `Pipeline` with `pipeline.start()`.
    4. Feed in each data to be processed by `pipeline.put(data)`.
    5. Signal `Pipeline` to wrap up with `pipeline.join()`
       when no more data is to be fed to it.

  The order of the operation units follows the order of `Pipe`s appended to the
  pipeline. Each `Pipe` owns a thread and runs in parallel. Queues are created
  to chain the `Pipe`s during the `build()` call, and only after then data may
  be fed to the pipeline. The `start()` method signals all the `Pipe`s to start
  operating. Data can be fed to the pipeline through `pipeline.put(data)`. Once
  `pipeline.join()` is called, the pipeline will no longer accept further data,
  and signals the underlying `Pipe`s to wrap up and shutdown once they have
  finished processing all the pending data, in series.

  Here is an example:

  The pipeline below does the following:
    1. Batch the numbers
    2. Add one to each number
    3. Form a pair (2*n-1, -n) for each number
    4. Print each pair

  ```python
  import tinypipe as tp

  def f1(nums):
    return [n + 1 for n in nums]

  def f2(nums):
    return [(2 * n - 1, -n) for n in nums]

  def f3(pairs):
    for pair in pairs:
      print("(%s, %s)" % pair)
    return pairs

  batch_pipe = tp.pipe.BatchPipe(100)
  func_pipe_1 = tp.pipe.FunctionPipe(f1)
  func_pipe_2 = tp.pipe.FunctionPipe(f2)
  func_pipe_3 = tp.pipe.FunctionPipe(f3)

  pipeline.append(batch_pipe)
  pipeline.append(func_pipe_1)
  pipeline.append(func_pipe_2)
  pipeline.append(func_pipe_3)
  # NOTE: One can call `pipeline.extend(pipes)` instead
  ```

  Build (optional) and start the pipeline:

  ```python
  pipeline.start()
  ```

  Feed data into the pipeline:

  ```python
  for i in range(2047):
    pipeline.put(i)
  ```

  When all data is fed into the pipeline, signal the pipeline to wrap up and
  stop once all data is processed.

  ```python
  pipeline.join()
  ```
  """
  def __init__(self, capacity=None, cooldown_secs=None):
    self._capacity = capacity
    self._cooldown_secs = cooldown_secs
    self._pipes = []

    self._lock = threading.Lock()
    self._chain = None
    self._qin = None

    self._built = False
    self._running = False
    self._join_called = False

  def append(self, pipe: pipe_lib.Pipe):
    if not isinstance(pipe, pipe_lib.Pipe):
      raise TypeError("`pipe` must be a `Pipe` instance. Given: {}"
                      .format(pipe))

    # TODO: Do we actually need a lock here?
    if not self._built:
      with self._lock:
        if not self._built:
          self._pipes.append(pipe)
          return
    logging.warning("No further pipe could be added after the pipeline has "
                    "been built. Ignoring pipe: {}".format(pipe))

  def extend(self, pipes: List[pipe_lib.Pipe]):
    [self.append(pipe) for pipe in pipes]

  def put(self, data):
    if not self._built:
      raise RuntimeError("Pipeline must be built to begin accepting data.")
    
    if self._join_called:
      logging.warning("No further data is accepted after `join()` is called. "
                      "Ignoring data: {}".format(data))
      return
    
    self._qin.put(data)

  def build(self):
    if self._built: return

    with self._lock:
      if self._built: return
      self._built = True
      self._qin = queue.Queue()
      self._chain = pipe_lib.ChainedPipe(self._pipes,
                                         capacity=self._capacity,
                                         cooldown_secs=self._cooldown_secs)
      self._chain.build(self._qin, None)

  def start(self):
    if not self._built:
      self.build()
    self._running = True
    self._chain.start()

  def join(self):
    if not self._running:
      logging.warning("Pipeline is not running. "
                      "The call `Pipeline.join()` has not effect.")
      return
    self._join_called = True
    self._chain.wrap_up()
    self._running = False
