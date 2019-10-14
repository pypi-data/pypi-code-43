from .query_component import QueryComponent
from ..query_result import IdsScoreQR
from ..utils import QueryParserValidator
import numpy as np

class Range(QueryComponent):
  op_name = 'range'
  def __init__(self, field, gt=None, gte=None, lt=None, lte=None):
    super().__init__('range')
    self.field = field
    self.gt = gt
    self.gte = gt
    self.lt = lt
    self.lte = lte

    self.ops = {
        'gt': np.greater,
        'gte': np.greater_equal,
        'lt': np.less,
        'lte': np.less_equal
    }

  def validate(self, index, score=False):
    if self.gt is None and self.gte is None and self.lt is None and self.lte is None:
      raise Exception('%s must have at least one of [gt, gte, lt, lte]' % self.name)
    
    if type(self.field) is not str:
      raise Exception('%s.field must be a string' % self.name)

    field_type = index.mapping.get_type(self.field)
    if field_type is None:
      raise Exception('%s.field %s - type not in mapping' % (self.name, self.field))

    if field_type not in {'integer', 'float'}:
      raise Exception('%s.field %s - cannot perform range on type (%s)' % (self.name, self.field, field_type))

    if self.gt is not None and not isinstance(self.gt, (float, int)):
      raise Exception('range.gt must be number when specified')

    if self.gte is not None and not isinstance(self.gte, (float, int)):
      raise Exception('range.gte must be number when specified')

    if self.lt is not None and not isinstance(self.lt, (float, int)):
      raise Exception('range.lt must be number when specified')

    if self.lte is not None and not isinstance(self.lte, (float, int)):
      raise Exception('range.lte must be number when specified')

    return True

  def execute(self, index, score=False):
    values = index.get_postings(self.field, None)
    range_mask = None

    bounds = {
      'gt': self.gt,
      'gte': self.gte,
      'lt': self.lt,
      'lte': self.lte,
    }

    for bound in bounds:
      if bounds[bound] is not None:
        op = self.ops.get(bound)
        mask = op(values.scores, bounds[bound])
        if range_mask is None:
          range_mask = mask
        else:
          range_mask = np.logical_and(range_mask, mask)
    return IdsScoreQR(values.ids[range_mask], 1)
  
  def required_rows(self, index, score=True):
    req_rows = set()
    req_rows.add((index.get_row_key(self.field, None), self.field))
    return req_rows
  
  @classmethod
  def from_json(cls, query, parse_query_fn):
    QueryParserValidator.is_single_value_dict(query, source=cls.op_name)
    field = [k for k in query][0]
    bounds = query[field]

    QueryParserValidator.is_dict(bounds, source=f'{cls.op_name}.{field}')
    QueryParserValidator.is_not_empty(bounds, source=f'{cls.op_name}.{field}')

    allowed_bounds = {'gt', 'gte', 'lt', 'lte'}
    for bound in bounds:
      QueryParserValidator.is_valid_op(bound, allowed_bounds, source=f'{cls.op_name}.{field}.{bound}')
      QueryParserValidator.is_number(bounds[bound], source=f'{cls.op_name}.{field}.{bound}')
    
    _gt = bounds.get('gt')
    _gte = bounds.get('gte')
    _lt = bounds.get('lt')
    _lte = bounds.get('lte')

    return cls(field, gt=_gt, gte=_gte, lt=_lt, lte=_lte)





    



