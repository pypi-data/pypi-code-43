import math

from .query_component import QueryComponent
from .term import Term
from ._or import Or
from ..query_result import EmptyQR, IdsScoreQR, IdsScoresQR
from ..low_level import sorted_multi_sum_scores
from ..utils import QueryParserValidator, QueryValidatorValidator

class _MatchHelper(QueryComponent):
  def __init__(self, field, value):
    super().__init__('_match_helpers')
    self.field = field
    self.value = value
  
  def execute(self, index, score=True):
    ids = index.get_postings(self.field, self.value).getIds()
    score = 1 / math.log(2 + ids.size)
    return IdsScoreQR(ids, score)

class Match(QueryComponent):
  op_name = 'match'
  def __init__(self, field, value, normalize=False):
    super().__init__('Match')
    self.field = field
    self.value = value
    self.normalize = normalize
  
  def validate(self, index, score=True):
    QueryValidatorValidator.is_str(self.field, source=f'{self.name}.field')
    QueryValidatorValidator.is_str(self.value, source=f'{self.name}.value')

    field_type = index.mapping.get_type(self.field)

    QueryValidatorValidator.is_not_none(field_type, source=f'{self.name}.field -> type')
    QueryValidatorValidator.is_valid_type(field_type, {'text', 'keyword'}, source=f'{self.name}.field -> type')
    return True

  def execute(self, index, score=True):
    tokens = index.analyze(self.field, self.value, return_text=False)

    if len(tokens):
      candidate_list = [_MatchHelper(self.field, token).execute(index, score=True) for token in tokens]
      ids_list = [e.getIds() for e in candidate_list]
      scores_list = [e.getScores() for e in candidate_list]
      ids, scores = sorted_multi_sum_scores(ids_list, scores_list, assume_sorted=True)
      if self.normalize:
        max_possible_score = 0
        for e in candidate_list:
          if e.getScores().size:
            max_possible_score += e.getScores()[0]
        if max_possible_score != 0:
          scores /= max_possible_score
      return IdsScoresQR(ids, scores)
    else:
      return EmptyQR()
  
  def required_rows(self, index, score=True):
    tokens = index.analyze(self.field, self.value, return_text=False)
    req_rows = set()
    for token in tokens:
      req_rows.add((index.get_row_key(self.field, token), self.field))
    return req_rows
  
  @classmethod
  def from_json(cls, query, parse_query_fn):
    QueryParserValidator.is_single_value_dict(query, source=cls.op_name)

    field = [k for k in query][0]
    value = query[field]

    QueryParserValidator.is_str(value, source=f'{cls.op_name}.{field}')

    return cls(field, value)

class NormalizedMatch(Match):
  op_name = 'normalized_match'
  def __init__(self, field, value):
    super().__init__(field, value, normalize=True)
    self.name = 'NormalizedMatch'