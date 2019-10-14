import json
import os
from .instance import Instance, Point


class InstanceReader:

    def _extract_name_from_path(self, path):
        return os.path.basename(path).split(".")[0]
        # return os.path.splitext(os.path.basename(path))[0]

    def from_raw(self, path):
        instance = Instance(name=self._extract_name_from_path(path))
        with open(path, 'r') as f:
            comment = ""
            for line in f:
                if '#' in line:
                    comment += line.replace("#", "").replace("\n", "")
                    continue
                tokens = line.split()
                if len(tokens) == 3:
                    i = int(tokens[0])
                    x = int(tokens[1])
                    y = int(tokens[2])
                    idx = instance.add_point(Point(x, y))
                    assert i == idx
            instance.meta_data["comment"] = comment
        return instance

    def to_json(self, path, instance: Instance):
        # if os.path.exists(path):
        #    raise FileExistsError(path + " already exists.")
        point_list = []
        for idx in range(len(instance)):
            p = instance[idx]
            point_list.append({"i": idx, "x": p.get_x(), "y": p.get_y()})
        d = dict()
        d['points'] = point_list
        d['type'] = "Instance"
        d['name'] = instance.name
        if instance.name != self._extract_name_from_path(path):
            print(f"Warning! Instance name {instance.name} does not",
                  f"fit the name of the file {path}!")
        if instance.meta_data:
            d['meta'] = instance.meta_data
        with open(path, "w") as f:
            json.dump(d, f, skipkeys=True)

    def from_json(self, path):
        name = str(self._extract_name_from_path(path))
        instance = Instance(name=name)
        with open(path, "r") as f:
            d = json.load(f)
            for p in d["points"]:
                idx = instance.add_point(Point(int(p["x"]), int(p["y"])))
                assert idx == int(p["i"])
            if 'meta' in d:
                instance.meta_data = d['meta']
            if 'name' in d:
                if d['name'] != name:
                    print(f"Warning! Instance name {d['name']} does not fit",
                          f"the name of the file {path}!")
        return instance
