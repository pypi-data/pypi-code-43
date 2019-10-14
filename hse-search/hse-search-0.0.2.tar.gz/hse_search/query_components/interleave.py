import functools

from .query_component import CompoundQuery
from ..query_result import IdsQR, IdsScoresQR
from ..low_level import sorted_intersect1d, sorted_multi_sum_scores_must

from ..utils import QueryValidatorValidator, QueryParserValidator

'''
{
  'interleave': {
    'queries': [
      {
        ...
      },
      {
        ...
      },
      {
        ...
      }
    ]
  }
}
'''

class Interleave(CompoundQuery):
  op_name = 'interleave'
  def __init__(self, sub_queries, window_size=100):
    super().__init__('Interleave', sub_queries)
    self.window_size = window_size
  
  def validate(self, index, score=True):
    QueryValidatorValidator.is_type(self.window_size, int, 'int', source=f'{self.name}.window_size')
    super().validate(index, score=score)
    return True
  
  def execute(self, index, score=True):
    candidate_list = [q.execute(index, score=score) for q in self.sub_queries]
    if score:
      ids_list = [e.getIds() for e in candidate_list]
      scores_list = [e.getScores() for e in candidate_list]
      ids, scores = sorted_multi_sum_scores_must(ids_list, scores_list, assume_sorted=True)
      return IdsScoresQR(ids, scores)
    else:
      candidate_list.sort(key=lambda x: x.getIds().size)
      return functools.reduce(lambda a, b: IdsQR(sorted_intersect1d(a.getIds(), b.getIds(), assume_sorted=True)), candidate_list)

  @classmethod
  def from_json(cls, query, parse_query_fn):
    QueryParserValidator.is_dict(query, source=cls.op_name)

    window_size = query.get(window_size, 100)
    QueryParserValidator.is_type(window_size, int, 'int', source=f'{cls.op_name}.window_size')

    queries = query.get('queries')
    QueryParserValidator.is_nonempty_list(queries, source=f'{cls.op_name}.queries')

    sub_queries = [parse_query_fn(subq, source=f'{self.op_name}.queries[:]') for subq in queries]

    return cls(sub_queries, window_size=window_size)