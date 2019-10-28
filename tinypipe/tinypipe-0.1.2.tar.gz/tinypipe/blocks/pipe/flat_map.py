from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import queue

from tinypipe.blocks.pipe import base as pipe_base


class FlatMapPipe(pipe_base.FetchRetryPipe):
  """Maps input and flattens the result.

  This `Pipe` is similar to `FunctionPipe` which calls the user provided
  function on each input. The result has to be an iterable which is then
  flattened to feed the output queue.

  For example, suppose we would like to load from a list of text files,
  line by line:

  ```python
  import tinypipe as tp

  def load_text_file(path):
    with open(path, "r") as fin:
      yield next(fin)

  pipe = tp.pipe.FlatMapPipe(load_text_file)

  pipeline = tp.Pipeline()
  pipeline.append(pipe)
  pipeline.start()
  """
  def __init__(self,
               fn,
               max_retry=None,
               fetch_time=None):
    super(FlatMapPipe, self).__init__(
        max_retry=max_retry, fetch_time=fetch_time)
    self._fn = fn

  def _run(self):
    try:
      data = self._fetch_data()
      it = self._fn(data)
      if not isinstance(it, collections.Iterable):
        raise RuntimeError("`fn` must return an iterable. Given: {}".format(it))
      if self._qout is not None:
        for out in it: self._qout.put(out)
      self._qin.task_done()
    except queue.Empty:
      pass
