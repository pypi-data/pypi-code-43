import re
from django.db.models import Manager
from django.db.models.query import QuerySet


def get_class_name(obj=None):
    # Get name of parent object.
    if obj is None:
        return "Unnamed"
    else:
        return obj.__class__.__name__


class HashableList(list):
    def __hash__(self):
        return id(self)


class HashableDict(dict):
    """
    Hashable Dictionary

    Hashables should be immutable -- not enforcing this but TRUSTING you not to mutate a
    dict after its first use as a key.

    https://stackoverflow.com/questions/1151658/python-hashable-dicts
    """

    def __hash__(self):
        vals = ()
        for v in self.values():
            try:
                hash(v)
                vals += (str(v),)
            except TypeError:
                if isinstance(v, list):
                    for x in v:
                        vals += (str(x),)
                else:
                    vals += (str(v),)
        return hash((frozenset(self), frozenset(vals)))


def normalize_path(path):
    if path.startswith("."):
        path = path[1:]
    if path.endswith("."):
        path = path[:-1]
    return path


def get_path_parts(obj, path, base_name=None):
    pattern = re.compile(r"(\w+\.\w+)")
    parts = [normalize_path(x) for x in pattern.split(path, 1) if len(x)]
    parts_final = []
    for part in parts:
        try:
            part_field = part.split(".")[1]
        except IndexError:
            part_field = part
        parts_final.append([part_field, part])

    ret = (parts_final[0][0], parts_final[0][1])
    if len(parts_final) > 1:
        ret += (parts_final[1][0], parts_final[1][1])
    else:
        ret += ("", "")
    return ret


def get_object(obj):
    if isinstance(obj, Manager):
        obj = obj.all()
    if isinstance(obj, QuerySet):
        obj = obj.first()
    return obj


class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """

    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.current_keys, self.past_keys = (
            set(current_dict.keys()),
            set(past_dict.keys()),
        )
        self.intersect = self.current_keys.intersection(self.past_keys)

    def added(self):
        """ Find keys that have been added """
        return self.current_keys - self.intersect

    def removed(self):
        """ Find keys that have been removed """
        return self.past_keys - self.intersect

    def changed(self):
        """ Find keys that have been changed """
        return set(
            o for o in self.intersect if self.past_dict[o] != self.current_dict[o]
        )

    def unchanged(self):
        """ Find keys that are unchanged """
        return set(
            o for o in self.intersect if self.past_dict[o] == self.current_dict[o]
        )

    def new_or_changed(self):
        """ Find keys that are new or changed """
        # return set(k for k, v in self.current_dict.items()
        #           if k not in self.past_keys or v != self.past_dict[k])
        return self.added().union(self.changed())


def remove_redundant_paths(paths):
    """
    Returns a list of unique paths.
    """
    results = []
    for path in paths:
        redundant = False
        paths_copy = paths[:]
        paths_copy.pop(paths.index(path))
        for p in paths_copy:
            if p.startswith(path) and len(p) > len(path):
                redundant = True
        if redundant is False:
            results.append(path)
    return results


def sort_field_paths(field_paths):
    """
    Clean up a list of field paths by removing duplicates, etc.
    """
    result = list(set(field_paths))
    result = remove_redundant_paths(result)
    result = [x for x in result if len(x)]
    return result
