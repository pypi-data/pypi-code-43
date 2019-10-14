import logging
from urllib import parse

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from redmin.models import Field
from redmin.rest.serializer.base import load_serializer_class, get_dynamic_serializer_class
from redmin.utils import import_class, attr, get_url_prefix

logger = logging.getLogger(__name__)


class BaseViewSet(viewsets.ModelViewSet):
    model = None

    def get_extra_action_url_map(self):
        ret = super().get_extra_action_url_map()
        url_prefix = get_url_prefix(self.request)
        for key in ret.keys():
            url = ret[key]
            parse_result = parse.urlparse(url)
            scheme, netloc = parse_result.scheme, parse_result.netloc
            ret[key] = url.replace(f"{scheme}://{netloc}", url_prefix)
        return ret

    def get_serializer_class(self):

        fields = [field.attribute for field in Field.get_fields(self.request.user, self.model) if "." not in field.attribute]
        return get_dynamic_serializer_class(self.model, fields)

    @action(methods=['GET'], detail=False)
    def schema(self, request):
        meta = self.metadata_class()
        data = meta.determine_metadata(request, self)
        return Response(data)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset

    def get_view_name(self):
        name = attr(self.model, "_meta.verbose_name")
        suffix = getattr(self, 'suffix', None)
        if suffix == "List":
            name += "(列表)"
        elif suffix == "Instance":
            name += "(实例)"

        return name


def load_viewset_class(model):
    app = model.__module__.split(".")[0]
    viewset_name = f"{model.__name__}ViewSet"
    serializer_class = load_serializer_class(model)
    search_fields = attr(model, "search_fields") or []
    filterset_fields = search_fields or serializer_class.Meta.fields
    try:
        clazz = import_class(f'{app}.rest.viewset.{viewset_name}')
        clazz.model = model
        if not attr(clazz, "serializer_class"):
            clazz.serializer_class = serializer_class
        if not attr(clazz, "queryset"):
            clazz.queryset = model.objects.all()
        if not attr(clazz, "filterset_fields"):
            clazz.filterset_fields = filterset_fields
        if not attr(clazz, "search_fields"):
            clazz.search_fields = search_fields
        logger.info(f"load rest viewset:{clazz}")
        return clazz
    except (AttributeError, ModuleNotFoundError):
        name = f"Dynamic{model.__name__}ViewSet"
        return type(name, (BaseViewSet,), dict(
            model=model,
            queryset=model.objects.all(),
            serializer_class=serializer_class,
            filterset_fields=filterset_fields,
            search_fields=search_fields,
            __module__=__name__
        ))
