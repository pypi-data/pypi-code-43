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


# base View model
class BaseReportListAPIView(LimitOffsetPaginationListAPIView):
    serializer_class = None
    model = None

    def get_model(self):
        if not self.model:
            raise NotImplementedError("model must be delcare")
        return self.model

    def get_queryset(self):
        admin = self.get_check_admin(self.request)
        integration_id = self.request.GET.get("integration_id")
        last_week = self.request.GET.get("last_week", "")
        last_3_days = self.request.GET.get("last_3_days", "")
        date_from = self.request.GET.get("date_from", "")
        date_to = self.request.GET.get("date_to", "")

        if not admin:
            raise PermissionDenied({"status": "error", "message": "This endpoint only for admin users."})

        if last_week == "true":
            date_to = datetime.datetime.today().strftime('%Y-%m-%d')
            last_date = datetime.datetime.today() - datetime.timedelta(days=7)
            date_from = last_date.strftime('%Y-%m-%d')
        elif last_3_days == "true":
            print("TUT")
            date_to = datetime.datetime.today().strftime('%Y-%m-%d')
            last_date = datetime.datetime.today() - datetime.timedelta(days=3)
            date_from = last_date.strftime('%Y-%m-%d')

        if not date_from and not date_to:
            raise NotAcceptable({"status": "error", "message": "miss data parametrs"})

        if integration_id:
            qs = self.get_model().objects.filter(integration_id=integration_id, date__range=[date_from, date_to])
        else:
            qs = self.get_model().objects.filter(date__range=[date_from, date_to])

        return qs


class HomeAPIView(CredentialMixin, APIView):
    def get(self, request, format=None):
        return Response({"status": "success", "message": "smart integration api"})
