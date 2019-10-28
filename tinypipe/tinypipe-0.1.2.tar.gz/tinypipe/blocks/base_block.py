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

import threading


class Block(threading.Thread):
  def __init__(self):
    super(Block, self).__init__()

    self._lock = threading.Lock()
    self._built = False
    self._running = False

  def _run(self):
    raise NotImplementedError("Must be implemented in descendants")

  def _ready_to_terminate(self):
    raise NotImplementedError("Must be implemented in descendants")

  def _build(self, *args, **kwargs):
    pass

  def build(self, *args, **kwargs):
    if self._built: return

    with self._lock:
      if self._built: return
      self._build(*args, **kwargs)
      self._built = True

  def run(self):
    if not self._built:
      raise RuntimeError("{} must be build before running."
                         .format(self.__class__.__name__))
    self._running = True
    while self._running or not self._ready_to_terminate():
      self._run()

  def wrap_up(self):
    self._running = False
