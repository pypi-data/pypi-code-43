from .query_component import QueryComponent
from ..query_result import IdsScoreQR
from ..utils import QueryParserValidator, QueryValidatorValidator

class Term(QueryComponent):
  op_name = 'term'
  def __init__(self, field, value):
    super().__init__('Term')
    self.field = field
    self.value = value
  
  def validate(self, index, score=True):
    QueryValidatorValidator.is_str(self.field, source=self.name)
    QueryValidatorValidator.is_str(self.value, source=self.name)

    field_type = index.mapping.get_type(self.field)

    QueryValidatorValidator.is_not_none(field_type, source=f'{self.name}.field -> type')
    QueryValidatorValidator.is_valid_type(field_type, {'text', 'keyword'}, source=f'{self.name}.field -> type')
    return True

  def execute(self, index, score=True):
    return IdsScoreQR(index.get_postings(self.field, self.value).getIds(), 1)
  
  def required_rows(self, index, score=True):
    req_rows = set()
    req_rows.add((index.get_row_key(self.field, self.value), self.field))
    return req_rows
  
  @classmethod
  def from_json(cls, query, parse_query_fn):
    QueryParserValidator.is_single_value_dict(query, source=cls.op_name)

    field = [k for k in query][0]
    QueryParserValidator.is_single_value_dict(query[field], source=f'{cls.op_name}.{field}')

    value = query[field].get('value')
    QueryParserValidator.is_str(value, source=f'{cls.op_name}.{field}.value')

    return cls(field, value)
