from ._and import And

class Filter(And):
  op_name = 'filter'
  def __init__(self, sub_queries):
    super().__init__(sub_queries, name='Filter')

  def execute(self, index, score=False):
    return super().execute(index, score=False)
