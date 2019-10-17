import numpy as np

from .query_component import QueryComponent
from ..query_result import IdsScoresQR
from ..utils import QueryValidatorValidator, QueryParserValidator

class FieldBoost(QueryComponent):
  op_name = 'field_boost'
  def __init__(self, field, boost):
    super().__init__('FieldBoost')
    self.field = field
    self.boost = boost
  
  def validate(self, index, score=True):
    QueryValidatorValidator.is_str(self.field, source=f'{self.name}.field')
    field_type = index.mapping.get_type(self.field)
    QueryValidatorValidator.is_not_none(field_type, source=f'{self.name}.field -> type')
    QueryValidatorValidator.is_valid_type(field_type, {'integer', 'float'}, source=f'{self.name}.field -> type')
    QueryValidatorValidator.is_number(self.boost, source=f'{self.name}.boost')
    return True
  
  def execute(self, index, score=True):
    a = index.get_postings(self.field, None)
    if self.boost != 1:
      b = IdsScoresQR(a.ids, np.array(a.scores, dtype=np.float32) * self.boost)
      return b
    else:
      return a
  
  def required_rows(self, index, score=True):
    req_rows = set()
    req_rows.add((index.get_row_key(self.field, None), self.field))
    return req_rows
  
  @classmethod
  def from_json(cls, query, parse_query_fn):
    QueryParserValidator.is_dict(query, source=cls.op_name)

    field = query.get('field')
    boost = query.get('boost')

    QueryParserValidator.is_str(field, source=f'{cls.op_name}.field')
    QueryParserValidator.is_number(boost, source=f'{cls.op_name}.boost')

    return cls(field, boost)
