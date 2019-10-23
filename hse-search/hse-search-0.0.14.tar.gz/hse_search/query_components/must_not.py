from ._and import And

class MustNot(And):
  '''
  Note, by itself, the must not filter behaves exactly like filter, meaning
  it does not do the 'not' part. In order to get the not of something, this
  op must be used with the Bool query so that it can be included with other
  criteria.
  '''
  op_name = 'must_not'
  def __init__(self, sub_queries):
    super().__init__(sub_queries, name='MustNot')

  def execute(self, index, score=False):
    return super().execute(index, score=False)
