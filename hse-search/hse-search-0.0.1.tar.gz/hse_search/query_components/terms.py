from .query_component import QueryComponent
from ._or import Or
from .term import Term
from ..utils import QueryParserValidator, QueryValidatorValidator

class Terms(QueryComponent):
  op_name = 'terms'
  def __init__(self, field, values):
    super().__init__('Terms')
    self.field = field
    self.values = values
  
  def validate(self, index, score=True):
    QueryParserValidator.is_str(self.field, source=f'{self.name}.field')
    QueryParserValidator.is_list_of_str(self.values, source=f'{self.name}.{self.field}[:]')

    field_type = index.mapping.get_type(self.field)
    QueryValidatorValidator.is_not_none(field_type, source=f'{self.name}.field -> {self.field}.type')

    QueryValidatorValidator.is_valid_type(field_type, {'text', 'keyword'}, source=f'{self.name}.field -> {self.field} ({field_type})')
    return True
  
  def execute(self, index, score=True):
    return Or([Term(self.field, value) for value in self.values]).execute(index, score=score)
  
  def required_rows(self, index, score=True):
    req_rows = set()
    for value in self.values:
      req_rows.add((index.get_row_key(self.field, value), self.field))
    return req_rows

  @classmethod
  def from_json(cls, query, parse_query_fn):
    QueryParserValidator.is_single_value_dict(query, source=cls.op_name)

    field = [k for k in query][0]

    QueryParserValidator.is_list_of_str(query[field], source=f'{cls.op_name}.{field}')

    value = query[field]
    return Terms(field, value)
