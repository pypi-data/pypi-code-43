import requests

from rest_framework.views import APIView
from django.http import HttpResponseRedirect
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotAcceptable

from integration_utils.mixins import CredentialMixin

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


class BaseGetCredentialAPIView(CredentialMixin, APIView):

    def get_redirect_uri(self):
        """Create in this method redirect uri
            Excample: https://oauth.yandex.ru/authorize?response_type=code&client_id={settings.YANDEX_APP_CLIENT_ID}&state={self.get_state()}&redirect_uri={redirect_url}
        """
        raise NotImplementedError()

    def check_auth_params(self):
        """This method for check auth params"""
        if "callback_url" not in self.request.GET \
                or "token" not in self.request.GET \
                or "platform_id" not in self.request.GET:
            raise PermissionDenied({"status": "error", "message": "You dont have permission to access."})
        return self.request

    def get_state(self):
        """
            Create state in this method
            Excample:
                user_info = self.get_user_info(request, get_token=True)
                user_id = user_info["id"]
                main_user = user_info["username"]
                # user_id = 16
                # main_user = "main_user"

                state = {
                    "callback_url": request.GET['callback_url'],
                    "user_id": user_id,
                    "main_user": main_user,
                    "platform_id": request.GET['platform_id']
                }
                return state
        """
        raise NotImplemented()

    def get(self, request, format=None):
        """
        ---
        parameters:
            - Authorization token in headers
            - 'callback_url' in GET params
        """

        return HttpResponseRedirect(self.get_redirect_uri())


class HomeAPIView(CredentialMixin, APIView):
    def get(self, request, format=None):
        return Response({"status": "success", "message": "smart integration api"})
