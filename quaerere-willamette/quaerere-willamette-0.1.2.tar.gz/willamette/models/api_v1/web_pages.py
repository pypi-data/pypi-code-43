__all__ = ['WebPageModel']
import logging


from arango_orm import Collection
from arango_orm.references import relationship
from willamette_common.schemas.api_v1.mixins import WebPageFieldsMixin

from .web_sites import WebSiteModel

LOGGER = logging.getLogger(__name__)


class WebPageModel(WebPageFieldsMixin, Collection):
    __collection__ = 'WebPages'
    _index = [
        {
            'type': 'hash',
            'fields': [
                'source_accounting.datetime_acquired',
                'source_accounting.data_origin',
                'url',
            ],
            'unique': True
        },
    ]

    web_site = relationship(WebSiteModel, 'web_site_key')
