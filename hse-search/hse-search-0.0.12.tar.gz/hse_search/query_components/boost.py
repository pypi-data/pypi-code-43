import numpy as np

from .query_component import QueryComponent
from ..query_result import IdsScoresQR
from ..utils import QueryParserValidator, QueryValidatorValidator

class Boost(QueryComponent):
  op_name = 'boost'
  def __init__(self, query, boost):
    super().__init__('Boost')
    self.query = query
    self.boost = boost
  
  def validate(self, index, score=True):
    QueryValidatorValidator.is_instance(self.query, QueryComponent, 'QueryComponent', source=f'{self.name}.query')
    QueryValidatorValidator.is_number(self.boost, source=f'{self.name}.boost')
    self.query.validate(index, score=score)
    return True

  def execute(self, index, score=True):
    a = self.query.execute(index, score=True)
    if self.boost != 1:
      b = IdsScoresQR(a.ids, np.array(a.scores, dtype=np.float32) * self.boost)
      return b
    else:
      return a
  
  def required_rows(self, index, score=True):
    return self.query.required_rows(index, score=True)

  @classmethod
  def from_json(cls, query, parse_query_fn):
    QueryParserValidator.is_dict(query, source=cls.op_name)

    q = query.get('query')
    boost = query.get('boost')

    QueryParserValidator.is_number(boost, source=f'{cls.op_name}.boost')

    return cls(parse_query_fn(q, source=f'{cls.op_name}.query'), boost)
