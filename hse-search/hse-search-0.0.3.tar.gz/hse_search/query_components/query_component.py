from ..query_result import EmptyQR
from ..utils import QueryParserValidator, QueryValidatorValidator

class QueryComponent:
  op_name = None
  def __init__(self, name):
    self.name = name
  
  def validate(self, index, score=True):
    try:
      assert type(self.name) is str
    except:
      raise Exception('QueryComponent must have name')
    return True

  def execute(self, index, score=True):
    return EmptyQR()
  
  def required_rows(self, index, score=True):
    return set()
  
  def from_json(value, parse_query_fn):
    return QueryComponent(None)

class CompoundQuery(QueryComponent):
  op_name = None
  def __init__(self, name, sub_queries):
    super().__init__(name)
    self.sub_queries = sub_queries
  
  def validate(self, index, score=True):
    super().validate(index, score=score)
    QueryValidatorValidator.is_nonempty_list(self.sub_queries, source=f'{self.name}[:]')
    
    for subq in self.sub_queries:
      QueryValidatorValidator.is_instance(subq, QueryComponent, 'QueryComponent', source=f'{self.name}[:]')
      subq.validate(index, score=score)
    return True
  
  def required_rows(self, index, score=True):
    req_rows = set()
    for q in self.sub_queries:
      rr = q.required_rows(index, score=score)
      req_rows = req_rows.union(rr)
    return req_rows
  
  @classmethod
  def from_json(cls, query, parse_query_fn):
    QueryParserValidator.is_nonempty_list(query, source=cls.op_name)
    
    for subq in query:
      QueryParserValidator.is_single_value_dict(subq, source=cls.op_name)
    
    sub_queries = [parse_query_fn(subq) for subq in query]

    return cls(sub_queries)
