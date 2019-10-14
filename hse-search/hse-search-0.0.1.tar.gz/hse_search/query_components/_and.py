import functools

from .query_component import CompoundQuery
from ..query_result import IdsQR, IdsScoresQR
from ..low_level import sorted_intersect1d, sorted_multi_sum_scores_must

class And(CompoundQuery):
  op_name = 'and'
  def __init__(self, sub_queries, name='And'):
    super().__init__(name, sub_queries)
  
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
