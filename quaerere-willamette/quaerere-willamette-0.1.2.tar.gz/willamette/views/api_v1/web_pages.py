__all__ = ['WebPageView']

from quaerere_base_flask.views.base import BaseView
from willamette_common.schemas.api_v1 import WebPageSchema

from willamette.app_util import ArangoDBMixin
from willamette.models.api_v1 import WebPageModel

WebPageSchema.model_class = WebPageModel


class WebPageView(ArangoDBMixin, BaseView):
    _obj_model = WebPageModel
    _obj_schema = WebPageSchema
