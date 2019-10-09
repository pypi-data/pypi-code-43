from __future__ import absolute_import

from lendsmart_api.objects import Base, Property


class LoanApplication(Base):

    api_endpoint = '/loan_documents'

    properties = {
        "id": Property(identifier=True),
        "created": Property(is_datetime=True),
        "updated": Property(is_datetime=True),
        "label": Property(mutable=True, filterable=True),
        "install_code": Property(),
        "apps": Property(),
        "api_key": Property(),
    }
