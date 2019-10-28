__all__ = ['WebSiteModel']

import logging

from arango_orm import Collection
from willamette_common.schemas.api_v1.mixins import WebSiteFieldsMixin

LOGGER = logging.getLogger(__name__)


class WebSiteModel(WebSiteFieldsMixin, Collection):
    __collection__ = 'WebSites'
    _index = [
        {'type': 'hash', 'fields': ['url', 'inLanguage'], 'unique': True}
    ]
