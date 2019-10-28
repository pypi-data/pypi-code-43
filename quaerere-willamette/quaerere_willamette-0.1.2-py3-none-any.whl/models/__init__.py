__all__ = ['get_collections', 'WebPageModelV1', 'WebSiteModelV1']

import sys, inspect

from arango_orm import Collection

from .api_v1 import WebPageModel as WebPageModelV1
from .api_v1 import WebSiteModel as WebSiteModelV1


def _model_classes():
    for cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
        if issubclass(cls[1], Collection) and cls[0] != 'Collection':
            yield cls[1]


def get_collections():
    for model in _model_classes():
        yield model
