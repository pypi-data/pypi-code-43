import inspect
import threading
from typing import List
from typing import Tuple
from typing import Type


class Annotations:
    def __init__(self):
        self._annotations_of_class = {}
        self._classes_by_annotation_name = {}
        self._lock = threading.Lock()

    def get_annotations_of_class(self, cls: Type) -> Tuple[str]:
        return tuple(self._annotations_of_class[cls])

    def get_classes_by_annotation_name(self, annotation_name: str) -> List[Type]:
        return list(self._classes_by_annotation_name[annotation_name])

    def annotate_class(self, cls: Type, annotation_name: str):
        with self._lock:
            if cls not in self._annotations_of_class:
                self._annotations_of_class[cls] = []
            self._annotations_of_class[cls].append(annotation_name)
            if annotation_name not in self._classes_by_annotation_name:
                self._classes_by_annotation_name[annotation_name] = []
            self._classes_by_annotation_name[annotation_name].append(cls)


def annotate(annotation_name):
    def wrapper(cls):
        if not inspect.isclass(cls):
            raise TypeError('Only classes can be annotated')
        annotations.annotate_class(cls, annotation_name)
        return cls
    return wrapper


annotations = Annotations()
