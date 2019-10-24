from rest_framework.viewsets import GenericViewSet
from rest_framework.serializers import Serializer
from rest_framework.response import Response
from nimblehelper.helper import NimbleHelper
from .utils import Utils
from .decorators import dynamic_log_level


class BaseView(GenericViewSet):
    def __placeholder_function(self, x_consumer_id, params, nim_headers=None):
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

    @dynamic_log_level()
    def list(self, request):
        nim_headers = Utils.get_nim_headers(request)
        params = NimbleHelper.check_get_parameters(request=request, fields=self.list_fields,
                                                   required_fields=self.list_required_fields)
        response = self.list_api_function(x_consumer_id=params["x_consumer_id"],
                                         params=params["data"], nim_headers=nim_headers)
        return Response(response, status=response["status"], headers=nim_headers)

    @dynamic_log_level()
    def create(self, request):
        nim_headers = Utils.get_nim_headers(request)
        params = NimbleHelper.check_post_parameters(request=request, fields=self.create_fields,
                                                    required_fields=self.create_required_fields)
        response = self.create_api_function(x_consumer_id=params["x_consumer_id"],
                                           params=params["data"], nim_headers=nim_headers)
        return Response(response, status=response["status"], headers=nim_headers)

    @dynamic_log_level()
    def retrieve(self, request, pk):
        nim_headers = Utils.get_nim_headers(request)
        params = NimbleHelper.check_get_parameters(request=request, fields=self.retrieve_fields,
                                                   required_fields=self.retrieve_required_fields, pk=pk)
        response = self.retrieve_api_function(x_consumer_id=params['x_consumer_id'], params=params['data'], nim_headers=nim_headers)
        return Response(response, status=response["status"], headers=nim_headers)

    @dynamic_log_level()
    def update(self, request, pk):
        nim_headers = Utils.get_nim_headers(request)
        params = NimbleHelper.check_put_parameters(request=request, fields=self.update_fields,
                                                   required_fields=self.update_required_fields, pk=pk)
        response = self.update_api_function(x_consumer_id=params['x_consumer_id'], params=params['data'], nim_headers=nim_headers)
        return Response(response, status=response["status"], headers=nim_headers)
