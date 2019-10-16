import json

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .edge_class import Edge  # pragma: no cover


class Node:

    def __init__(self,
                 id: str,
                 attributes: Optional[dict] = None):
        self.id = id
        self.attributes = attributes or {}
        self.target_neighbors = {}
        self.source_neighbors = {}
        self.neighbors = {}

    def get_dict(self) -> dict:
        if self.attributes:
            optionals = {'attributes': self.attributes}
        else:
            optionals = {}
        return {
            'type': 'node',
            'id': self.id,
            **optionals
        }

    def add_edge(self, e: 'Edge'):

        if e.source == self.id:
            neighbor_id = e.target
            relevant_dict = self.target_neighbors
        elif e.target == self.id:
            neighbor_id = e.source
            relevant_dict = self.source_neighbors
        else:
            raise ValueError("Trying to add an edge to node {} whose ends are source: {} target: {}"
                             .format(self.id, e.source, e.target))

        for d in [relevant_dict,
                  self.neighbors]:

            try:
                d[neighbor_id].append(e)
            except KeyError:
                d[neighbor_id] = [e]

    def _comparison_neighbors(self, way: str):

        if way == 'in':
            edge_dic = self.source_neighbors
        else:
            edge_dic = self.target_neighbors

        return {n: sorted([json.dumps(e.get_dict(),
                                      sort_keys=True,
                                      indent=0)
                          for e in el])
                for n, el in edge_dic.items()}

    def get_inward_comparison_neighbors(self):
        return self._comparison_neighbors('in')

    def get_outward_comparison_neighbors(self):
        return self._comparison_neighbors('out')
