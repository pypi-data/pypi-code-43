"""


## TODO:
- streaming
- parallelize with thread or process pool and queues
- translate into airflow DAG
- auto device transfer
"""

class Op:
  device = None

  sources = []
  targets = []

  def __init__(self, *args, **kwargs):
    pass

  def __lshift__(self, other):
    pass

  def __rshift__(self, other):
    pass

  def __lt__(self, other):
    pass

  def __gt__(self, other):
    pass

  def __call__(self, *args, **kwargs):
    pass


class Feed(Op):
  pass

class Sink(Op):
  pass

class ReadParquet(Feed):
  pass

class SaveParquet(Sink):
  pass


class Cache(Sink, Feed):
  pass

class BatchOp(Op):
  pass

class SampleOp(Op):
  pass


class Batcher(Op):
  pass

class Splitter(Op):
  pass

class Collate(Op):
  pass



class Pipeline(Op):
  pass



class LoadImage(SampleOp):
  pass


class StackTensors(Collate):
  pass


class TransformImage(SampleOp):
  pass

class ApplyModule(BatchOp):
  pass

class SaveTensors(BatchOp):
  pass

class Glob(Feed):
  pass


class ParquetDataset(Feed, Sink):
  pass


preprocess = (
  ReadParquet()
  > LoadImage()
  > TransformImage()
  >> StackTensors()
)


disk = preprocess > SaveTensors()

infrence = (
    preprocess
    > ApplyModule('resnet')
    > SaveTensors()
)


train = (

)


test = (

)

evaluate = (

)