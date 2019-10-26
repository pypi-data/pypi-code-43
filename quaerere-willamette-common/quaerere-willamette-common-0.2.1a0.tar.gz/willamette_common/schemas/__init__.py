__all__ = ['WebPageFieldsMixinV1', 'WebPageSchemaV1', 'WebSiteFieldsMixinV1', 'WebSiteSchemaV1']

from .api_v1 import WebPageSchema as WebPageSchemaV1
from .api_v1 import WebSiteSchema as WebSiteSchemaV1
from .api_v1.mixins import WebPageFieldsMixin as WebPageFieldsMixinV1
from .api_v1.mixins import WebSiteFieldsMixin as WebSiteFieldsMixinV1
