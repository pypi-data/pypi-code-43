from ._or import Or

class Should(Or):
  op_name = 'should'
  def __init__(self, sub_queries):
    super().__init__(sub_queries, name='Should')

  def execute(self, index, score=True):
    return super().execute(index, score=True)
