from django.urls import include, path

from .pagination import RedminPagination
from .permission import RolePermission
from .view import account


def get_rest_patterns(prefix):
    from redmin.rest.router import BaseRouter
    from redmin.rest.serializer.base import BaseSerializer
    from redmin.rest.viewset.base import BaseViewSet, load_viewset_class
    from redmin.rest.utils import get_all_models
    r = BaseRouter()
    for model in get_all_models():
        viewset = load_viewset_class(model)
        r.register(model.__name__, viewset)

    account_methods = ["login", "logout", "token", "profile"]
    account_patterns = [path(f'{prefix}/account/{method}', getattr(account, method), name=f"account-{method}") for method in account_methods]
    return account_patterns + [
        path(f'{prefix}/auth/', include('rest_framework.urls')),
        path(f'{prefix}/', include(r.urls)),
    ]
