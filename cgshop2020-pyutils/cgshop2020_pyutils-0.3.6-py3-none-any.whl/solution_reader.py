import json
import os
from typing import List, Union
from .solution import Solution, Edge


class SolutionReaderError(Exception):
    def __init__(self, message):
        self.file = None
        self.instance_name = None
        super().__init__(message)


class WrongJSONType(SolutionReaderError):
    def __init__(self, message):
        super().__init__(message)


class WrongObjectType(SolutionReaderError):
    def __init__(self):
        super().__init__('Solution object does not have "type": "Solution"!')


class MissingInstanceName(SolutionReaderError):
    def __init__(self):
        super().__init__('Solution object does not have an instance name!')


class MissingEdges(SolutionReaderError):
    def __init__(self, instance_name):
        super().__init__("Solution object for instance '{}' does not have edges!".format(instance_name))
        self.instance_name = instance_name


class InvalidEdge(SolutionReaderError):
    def __init__(self, instance_name):
        super().__init__("Solution object for instance '{}' contains an invalid edge!".format(instance_name))
        self.instance_name = instance_name


class SolutionReader:
    def _check_type(self, json_dict: dict):
        if "type" not in json_dict or json_dict["type"].lower() != "solution":
            raise WrongObjectType()

    def _check_instance_name(self, json_dict: dict):
        if "instance_name" not in json_dict or\
           not isinstance(json_dict["instance_name"], str) or\
           not json_dict["instance_name"]:
            raise MissingInstanceName()

    def _check_edge(self, json_dict, edge):
        try:
            int(edge["i"])
            int(edge["j"])
        except Exception as e:
            raise InvalidEdge(json_dict["instance_name"]) from e

    def _check_edges(self, json_dict: dict):
        if "edges" not in json_dict or not isinstance(json_dict["edges"], list) or not json_dict["edges"]:
            raise MissingEdges(json_dict["instance_name"])
        for e in json_dict["edges"]:
            self._check_edge(json_dict, e)

    def _set_file_name(self, solutions: Union[Solution, List[Solution]], file_name):
        if isinstance(solutions, list):
            for s in solutions:
                s.meta_data["file_name"] = file_name
        else:
            solutions.meta_data["file_name"] = file_name
        return solutions

    def from_json_list(self, json_list: list) -> List[Solution]:
        for d in json_list:
            if not isinstance(d, dict):
                raise WrongJSONType("List of solution objects contains invalid elements!")
        return [self.from_json_dict(d) for d in json_list]

    def from_json_dict(self, json_dict: dict) -> Solution:
        self._check_type(json_dict)
        self._check_instance_name(json_dict)
        self._check_edges(json_dict)

        solution = Solution(instance=json_dict["instance_name"])
        for edge in json_dict["edges"]:
            solution.add_edge(Edge(int(edge["i"]), int(edge["j"])))
        if 'meta' in json_dict:
            solution.meta_data = json_dict["meta"]  # otherwise, keep the empty dict from Solution.__init__
        return solution

    def from_json_object(self, json_data, file_name=None) -> Union[Solution, List[Solution]]:
        try:
            if isinstance(json_data, dict):
                return self.from_json_dict(json_data)
            elif isinstance(json_data, list):
                return self.from_json_list(json_data)
            else:
                raise WrongJSONType("Document does not contain a solution object nor a list of such objects!")
        except SolutionReaderError as e:
            e.file = file_name
            raise e

    def from_json_text(self, content: str, file_name=None) -> Union[Solution, List[Solution]]:
        json_data = json.JSONDecoder().decode(content)
        try:
            return self._set_file_name(self.from_json_object(json_data), file_name)
        except SolutionReaderError as e:
            e.file = file_name
            raise e

    def from_json_file(self, path: Union[str, os.PathLike]) -> Union[Solution, List[Solution]]:
        with open(path, "r") as file:
            json_data = json.load(file)
            try:
                return self._set_file_name(self.from_json_object(json_data), path)
            except SolutionReaderError as e:
                e.file = path
                raise e
