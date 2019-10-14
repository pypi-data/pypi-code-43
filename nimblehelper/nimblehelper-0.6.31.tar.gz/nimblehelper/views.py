from rest_framework.viewsets import GenericViewSet
from rest_framework.serializers import Serializer
from rest_framework.response import Response
from nimblehelper.helper import NimbleHelper
from .utils import Utils


class BaseView(GenericViewSet):
    @staticmethod
    def __placeholder_function(x_consumer_id, params, nim_headers=None):
        if not nim_headers:
            nim_headers = dict()
        return {'status': 500, 'x_consumer_id': x_consumer_id, 'params': params, 'nim_headers': nim_headers}

    serializer_class = Serializer

    list_api_function = __placeholder_function
    list_fields = []
    list_required_fields = []

    create_api_function = __placeholder_function
    create_fields = []
    create_required_fields = []

    retrieve_api_function = __placeholder_function
    retrieve_fields = []
    retrieve_required_fields = []

    update_api_function = __placeholder_function
    update_fields = []
    update_required_fields = []

    @classmethod
    def list(cls, request):
        nim_headers = Utils.get_nim_headers(request)
        params = NimbleHelper.check_get_parameters(request=request, fields=cls.list_fields,
                                                   required_fields=cls.list_required_fields)
        response = cls.list_api_function(x_consumer_id=params["x_consumer_id"],
                                         params=params["data"], nim_headers=nim_headers)
        return Response(response, status=response["status"], headers=nim_headers)

    @classmethod
    def create(cls, request):
        nim_headers = Utils.get_nim_headers(request)
        params = NimbleHelper.check_post_parameters(request=request, fields=cls.create_fields,
                                                    required_fields=cls.create_required_fields)
        response = cls.create_api_function(x_consumer_id=params["x_consumer_id"],
                                           params=params["data"], nim_headers=nim_headers)
        return Response(response, status=response["status"], headers=nim_headers)

    @classmethod
    def retrieve(cls, request, pk):
        nim_headers = Utils.get_nim_headers(request)
        params = NimbleHelper.check_get_parameters(request=request, fields=cls.retrieve_fields,
                                                   required_fields=cls.retrieve_required_fields, pk=pk)
        response = cls.retrieve_api_function(x_consumer_id=params['x_consumer_id'], params=params['data'], nim_headers=nim_headers)
        return Response(response, status=response["status"], headers=nim_headers)

    @classmethod
    def update(cls, request, pk):
        nim_headers = Utils.get_nim_headers(request)
        params = NimbleHelper.check_put_parameters(request=request, fields=cls.update_fields,
                                                   required_fields=cls.update_required_fields, pk=pk)
        response = cls.update_api_function(x_consumer_id=params['x_consumer_id'], params=params['data'], nim_headers=nim_headers)
        return Response(response, status=response["status"], headers=nim_headers)
