__all__ = ['WebSiteView']

from quaerere_base_flask.views.base import BaseView
from willamette_common.schemas.api_v1 import WebSiteSchema

from willamette.models.api_v1 import WebSiteModel
from willamette.app_util import ArangoDBMixin

WebSiteSchema.model_class = WebSiteModel


class WebSiteView(ArangoDBMixin, BaseView):
    _obj_model = WebSiteModel
    _obj_schema = WebSiteSchema
