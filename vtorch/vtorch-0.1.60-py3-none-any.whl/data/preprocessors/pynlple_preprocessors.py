from pynlple.processing import preprocessor
from itertools import chain
from typing import List


def get_pynlple_preprocessors(pynlple_preprocessors_attr: List) -> List[preprocessor.IPreprocessor]:
    pynlple_preprocessors = []
    for method, *args in pynlple_preprocessors_attr:
        pynlple_preprocessors.append(getattr(preprocessor, method)(*list(chain(*args))))
    return pynlple_preprocessors
