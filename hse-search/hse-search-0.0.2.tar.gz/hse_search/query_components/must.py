from ._and import And

class Must(And):
  op_name = 'must'
  def __init__(self, sub_queries):
    super().__init__(sub_queries, name='Must')
  
  def execute(self, index, score=True):
    return super().execute(index, score=True)
