import functools
import numpy as np

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
    candidate_list = [q.execute(index, score=score).getTopN(self.window_size) for q in self.sub_queries]

    ids = []
    scores = []

    num_queries = len(candidate_list)

    curr_score = self.window_size * num_queries

    for i in range(self.window_size):
        for j in range(num_queries):
            if i < len(candidate_list[j][0]):
                ids.append(candidate_list[j][0][i])
                scores.append(curr_score)
                curr_score -= 1
    
    return IdsScoresQR(np.array(ids, dtype=np.int32), np.array(scores, dtype=np.float32))
    


  @classmethod
  def from_json(cls, query, parse_query_fn):
    QueryParserValidator.is_dict(query, source=cls.op_name)

    window_size = query.get('window_size', 100)
    QueryParserValidator.is_type(window_size, int, 'int', source=f'{cls.op_name}.window_size')

    queries = query.get('queries')
    QueryParserValidator.is_nonempty_list(queries, source=f'{cls.op_name}.queries')

    sub_queries = [parse_query_fn(subq, source=f'{cls.op_name}.queries[:]') for subq in queries]

    return cls(sub_queries, window_size=window_size)