from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotAcceptable, MethodNotAllowed

from integration_utils.mixins import CredentialMixin
from .models import BaseAPIMethod, CustomAPIMethod
from .serializers import BaseAPIMethodSerializer, CustomAPIMethodSerializer


class BaseMethodModelViewSet(CredentialMixin, ModelViewSet):
    serializer_class = BaseAPIMethod

    def get_object(self, *args, **kwargs):
        if self.request.GET.get("dashboard", "").lower() == "true":
            _ = self.get_check_dash_auth(self.request)
        else:
            _ = self.get_user_info(self.request)
        pk = self.kwargs.get('pk')
        try:
            method = BaseAPIMethod.objects.get(id=pk)
        except BaseAPIMethod.DoesNotExist:
            raise MethodNotAllowed(method_name, {
                "status": "error",
                "message": f"Base Method '{method_name}' does not exist."})

        return method

    def get_queryset(self, *args, **kwargs):
        if self.request.GET.get("dashboard", "").lower() == "true":
            _ = self.get_check_dash_auth(self.request)
        else:
            _ = self.get_user_info(self.request)
        qs = BaseAPIMethod.objects.all()

        return qs

    def create(self, request, *args, **kwargs):
        """
        create basic method
        ---
        params:
        - Authorization token in headers
        - name in DATA
        - endpoint in DATA
        - request_method in DATA
        - definition in DATA
        definition(params key): 
        - default: {}
        - change_keys: {}
        """
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        list of basic retail methods
        ---
        params:
        - Authorization token in headers
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        detail basic retail method
        ---
        params:
        - Authorization token in headers
        """
        return super().retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        try:
            BaseAPIMethod.objects.get(id=pk).delete()
            return Response({"status": "success"})
        except BaseAPIMethod.DoesNotExist:
            return Response({"status": "error", "message": "invalid method"}, status=422)

    def update(self, request, *args, **kwargs):
        """
        update basic method
        ---
        params:
        - Authorization token in headers
        - name in DATA
        - endpoint in DATA
        - request_method in DATA
        - definition in DATA
        definition(params key): 
        - default: {}
        - change_keys: {}
        """
        return super(BaseAPIMethod, self).update(request, *args, **kwargs)


class CustomAPIMethodViewSet(CredentialMixin, ModelViewSet):
    serializer_class = CustomAPIMethodSerializer

    def get_object(self, *args, **kwargs):
        if self.request.GET.get("dashboard", "").lower() == "true":
            _ = self.get_check_dash_auth(self.request)
        else:
            _ = self.get_user_info(self.request)
        pk = self.kwargs.get("pk")

        try:
            method = CustomAPIMethod.objects.get(id=pk)
        except CustomAPIMethod.DoesNotExist:
            raise MethodNotAllowed(method_name, {
                "status": "error",
                "message": f"Custom Method '{method_name}' does not exist."
            })

        return method

    def get_queryset(self, *args, **kwargs):
        if self.request.GET.get("dashboard", "").lower() == "true":
            _ = self.get_check_dash_auth(self.request)
        else:
            _ = self.get_user_info(self.request)
        qs = CustomAPIMethod.objects.all()

        return qs

    def create(self, request, *args, **kwargs):
        """
        create custom method
        ---
        params:
        - Authorization token in headers
        - name in DATA
        - config in DATA
        - definition in DATA
        config(parameters key):
        - methods in keys(methods must be NAMES from base api methods)
        """
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        list of custom methods
        ---
        params:
        - Authorization token in headers
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        detail custom method
        ---
        params:
        - Authorization token in headers
        """
        return super().retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        try:
            CustomAPIMethod.objects.get(id=pk).delete()
            return Response({"status": "success"})
        except CustomAPIMethod.DoesNotExist:
            return Response({"status": "error", "message": "invalid method"}, status=422)

    def update(self, request, *args, **kwargs):
        """
        update custom method
        ---
        params:
        - Authorization token in headers
        - name in DATA
        - config in DATA
        - definition in DATA
        config(parameters key):
        - methods in keys(methods must be NAMES from base api methods)
        """
        return super().update(request, *args, **kwargs)
