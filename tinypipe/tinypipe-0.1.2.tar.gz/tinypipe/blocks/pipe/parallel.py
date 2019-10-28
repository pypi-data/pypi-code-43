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

import time

from tinypipe.blocks.pipe import base as base_pipe
from tinypipe.utils import general as gen_utils


class ParallelPipe(base_pipe.Pipe):
  """Identical copies of `Pipe` arranged in parallel.

  Each pipe runs in an individual thread, sharing the same input and output
  queues. Therefore, the theoretical throughput of this pipe would be
  `num_parallel_pipes` times that of a single one.

  A zero-argument `pipe_init_fn` that creates a new `Pipe` instance is expected.
  This could be simply a lambda-wrapped constructor call. For instance:

  ```python
  import tinypipe as tp

  def f(data):
    ...
    return result

  init_fn = lambda: tp.pipe.FunctionPipe(f)
  pipe = tp.pipe.ParallelPipe(init_fn, num_parallel_pipes=4)

  pipeline = tp.Pipeline()
  pipeline.append(pipe)
  pipeline.start()
  ```
  """
  def __init__(self,
               pipe_init_fn,
               num_parallel_pipes=None,
               cooldown_secs=None):
    # TODO: Add validation logic:
    # 1. `pipe_init_fn`: Function that takes no argument, returns a new `Pipe`
    # 2. `num_pipes`: Positive integer
    # 3. `cooldown_secs`: positive float
    test_pipe = pipe_init_fn()
    if not isinstance(test_pipe, base_pipe.Pipe):
      raise TypeError("`pipe_init_fn` must be a zero-argument function "
                      "that returns a `Pipe` instance. Object returned: {}"
                      .format(type(test_pipe)))
    del test_pipe

    super(ParallelPipe, self).__init__()
    self._pipes = []
    self._pipe_init_fn = pipe_init_fn
    self._num_parallel_pipes = gen_utils.val_or_default(num_parallel_pipes, 1)
    self._cooldown_secs = gen_utils.val_or_default(cooldown_secs, 0.1)

  def _run(self):
    time.sleep(self._cooldown_secs)

  def _ready_to_terminate(self):
    return not any(p.is_alive() for p in self._pipes)

  def _build_pipe(self):
    # TODO: Add validation logic
    for _ in range(self._num_parallel_pipes):
      p = self._pipe_init_fn()
      p.build(self._qin, self._qout)
      self._pipes.append(p)

  def start(self):
    [p.start() for p in self._pipes]
    super(ParallelPipe, self).start()

  def wrap_up(self):
    [p.wrap_up() for p in self._pipes]
    super(ParallelPipe, self).wrap_up()
