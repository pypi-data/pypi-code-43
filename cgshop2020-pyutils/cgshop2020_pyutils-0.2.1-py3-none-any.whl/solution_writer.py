import datetime
import json
import os
from .solution import Solution, Edge
from .solution_reader import SolutionReader


class SolutionWriter:
    def to_json(self, solution: Solution, path, include_meta=True):
        if os.path.exists(path):
            raise FileExistsError(path + " already exists.")
        with open(path, "w") as file:
            json_dict = self._create_json_dict(solution, include_meta=include_meta)
            json.dump(fp=file, obj=json_dict, skipkeys=True)

    def _create_json_dict(self, solution, include_meta) -> dict:
        json_dict = dict()
        json_dict["type"] = "Solution"
        json_dict["instance_name"] = solution.instance_name
        if include_meta:
            if 'date' not in solution.meta_data:
                solution.meta_data['date'] = datetime.datetime.now().strftime("%Y-%m-%d")
            json_dict["meta"] = solution.meta_data
        json_dict["edges"] = self._get_json_edge_list(solution)
        return json_dict

    def _get_json_edge_list(self, solution):
        json_list = []
        for edge in solution:
            json_list.append({"i": edge.get_i(), "j": edge.get_j()})
        return json_list

    # for backwards compatibility, forward to SolutionReader
    def from_json(self, path) -> Solution:
        return SolutionReader().from_json_file(path)
