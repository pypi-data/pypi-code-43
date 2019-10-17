from .query_component import CompoundQuery
from ..query_result import IdsQR, IdsScoresQR
from ..low_level import sorted_multi_sum_scores, sorted_multi_union1d

class Or(CompoundQuery):
  op_name = 'or'
  def __init__(self, sub_queries, name='Or'):
    super().__init__(name, sub_queries)
  
  def execute(self, index, score=True):
    candidate_list = [q.execute(index, score=score) for q in self.sub_queries]
    if score:
      ids_list = [e.getIds() for e in candidate_list]
      scores_list = [e.getScores() for e in candidate_list]
      ids, scores = sorted_multi_sum_scores(ids_list, scores_list, assume_sorted=True)
      return IdsScoresQR(ids, scores)
    else:
      ids_list = [e.getIds() for e in candidate_list]
      return IdsQR(sorted_multi_union1d(ids_list, assume_sorted=True))
