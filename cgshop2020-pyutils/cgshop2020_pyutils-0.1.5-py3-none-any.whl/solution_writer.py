import datetime
import json
import os

from .solution import Solution, Edge


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

    def from_json(self, path):
        with open(path, "r") as file:
            json_dict = json.load(file)
            solution = Solution(instance=json_dict["instance_name"])
            for edge in json_dict["edges"]:
                solution.add_edge(Edge(int(edge["i"]), int(edge["j"])))
            if 'meta' in json_dict:
                solution.meta_data = json_dict["meta"]
        return solution

    def _get_json_edge_list(self, solution):
        json_list = []
        for edge in solution:
            json_list.append({"i": edge.get_i(), "j": edge.get_j()})
        return json_list
