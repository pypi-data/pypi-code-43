import requests
import datetime

from rest_framework.views import APIView
from django.http import HttpResponseRedirect
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotAcceptable

from integration_utils.mixins import CredentialMixin
from integration_utils.pagination import LimitOffsetPaginationListAPIView

from .models import Credential
from .serializers import CredentialSerializer


class BaseCredentialModelViewSet(CredentialMixin, ModelViewSet):
    queryset = Credential.objects.all()
    serializer_class = CredentialSerializer

    def create(self, request, format=None):
        raise NotImplementedError()

    def retrieve(self, request, *args, **kwargs):
        """
        ---
        parameters:
            - Authorization token in headers
        """

        _ = self.get_check_dash_auth(request)
        return super().retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        ---
        parameters:
            - Authorization token in headers
        """
        _ = self.get_check_dash_auth(request)

        return super().list(request, *args, **kwargs)


class HomeAPIView(CredentialMixin, APIView):
    def get(self, request, format=None):
        return Response({"status": "success", "message": "smart integration api"})
