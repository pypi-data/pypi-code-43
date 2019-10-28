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
import time

from tinypipe.blocks.pipe import base as base_pipe
from tinypipe.utils import general as gen_utils


class ChainedPipe(base_pipe.Pipe):
  def __init__(self,
               pipes,
               capacity=None,
               cooldown_secs=None):
    # TODO: Add validation logic:
    # 1. `pipes`: non-empty list of non-built `Pipe`s
    # 2. `capacity`: non-negative integer
    # 3. `cooldown_secs`: positive float
    super(ChainedPipe, self).__init__()
    self._pipes = pipes
    self._capacity = gen_utils.val_or_default(capacity, 0)
    self._cooldown_secs = gen_utils.val_or_default(cooldown_secs, 0.05)

  def _run(self):
    time.sleep(self._cooldown_secs)

  def _ready_to_terminate(self):
    return not any(p.is_alive() for p in self._pipes)

  def _build_pipe(self):
    qin = self._qin
    for i in range(len(self._pipes) - 1):
      p = self._pipes[i]
      qout = queue.Queue(maxsize=self._capacity)
      p.build(qin, qout)
      qin = qout
    self._pipes[-1].build(qin, self._qout)

  def start(self):
    [p.start() for p in self._pipes]
    super(ChainedPipe, self).start()

  def wrap_up(self):
    [p.wrap_up() for p in self._pipes]
    super(ChainedPipe, self).wrap_up()
