from kyc.operations.get import GetOperation
from kyc.operations.list import ListOperation
from kyc.util import Util
from .model_base import ModelBase
from .data import Data


class Datatable(GetOperation, ListOperation, ModelBase):

    @classmethod
    def get_path(cls):
        return "%s/metadata" % cls.default_path()

    def data(self, **options):
        updated_options = Util.convert_options(**options)
        return Data.page(self, **updated_options)
