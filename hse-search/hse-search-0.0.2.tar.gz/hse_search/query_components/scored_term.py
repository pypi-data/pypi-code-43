from .query_component import QueryComponent
from ..utils import QueryParserValidator, QueryValidatorValidator

class ScoredTerm(QueryComponent):
  op_name = 'scored_term'
  def __init__(self, field, value):
    super().__init__('scored_term')
    self.field = field
    self.value = value
  
  def validate(self, index, score=True):
    super().validate(index, score=score)
    QueryValidatorValidator.is_str(self.field, source=f'{self.name}.field')
    QueryValidatorValidator.is_str(self.value, source=f'{self.name}.value')
    
    field_type = index.mapping.get_type(self.field)
    QueryValidatorValidator.is_not_none(self.field, source=f'{self.name}.field -> type')
    QueryValidatorValidator.is_valid_type(field_type, {'scored_keyword'}, source=f'{self.name}.field -> type')
    return True

  def execute(self, index, score=True):
    return index.get_postings(self.field, self.value)
  
  def required_rows(self, index, score=True):
    req_rows = set()
    req_rows.add((index.get_row_key(self.field, self.value), self.field))
    return req_rows
  
  @classmethod
  def from_json(cls, query, parse_query_fn):
    QueryValidatorValidator.is_dict(query, source=cls.op_name)
    field = query.get('field')
    value = query.get('value')

    QueryValidatorValidator.is_str(field, source=f'{cls.op_name}.field')
    QueryValidatorValidator.is_str(value, source=f'{cls.op_name}.value')

    return cls(field, value)
