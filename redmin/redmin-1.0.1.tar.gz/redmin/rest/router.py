from collections import OrderedDict
from urllib import parse

from django.urls import NoReverseMatch
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.routers import DefaultRouter, APIRootView

from redmin.models import Permission, PermissionItem
from redmin.rest.utils import get_all_model_map
from redmin.utils import get_url_prefix, attr

permission_items = [item for item in vars(PermissionItem).keys() if "_" not in item]


class _RootView(APIRootView):
    """
    Cinema Restful API
    """

    def get_view_name(self):
        return "影院后台列表"

    def get(self, request, *args, **kwargs):
        ret = OrderedDict()
        namespace = request.resolver_match.namespace
        url_prefix = get_url_prefix(request)
        all_models = get_all_model_map()
        for model_name, url_name in self.api_root_dict.items():
            model = all_models.get(model_name, None)
            permission: PermissionItem = Permission.get_permission(request.user, model)
            if not model or not permission or not permission.viewable:
                continue

            if namespace:
                url_name = namespace + ':' + url_name
            try:
                url = reverse(url_name, args=args, kwargs=kwargs, request=request, format=kwargs.get('format', None))
                parse_result = parse.urlparse(url)
                scheme, netloc = parse_result.scheme, parse_result.netloc
                ret[model_name] = {
                    "url": url.replace(f"{scheme}://{netloc}", url_prefix),
                    "permission": {item: attr(permission, item) for item in permission_items}
                }
            except NoReverseMatch:
                continue
        return Response(ret)


class BaseRouter(DefaultRouter):
    APIRootView = _RootView
