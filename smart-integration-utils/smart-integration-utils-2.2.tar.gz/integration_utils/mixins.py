import requests
from urllib.parse import unquote

from rest_framework.exceptions import PermissionDenied
from django.conf import settings


class CredentialMixin(object):
    if settings.DASHBOARD_URL.endswith("/"):
        url = settings.DASHBOARD_URL
    else:
        url = settings.DASHBOARD_URL + '/'

    def get_user_info(self, request, get_token=False, *args, **kwargs):
        if get_token:
            token = unquote(request.GET["token"])
        else:
            if 'HTTP_ZAPPA_TOKEN' in request.META:  # check query from EM server
                if request.META['HTTP_ZAPPA_TOKEN'] == settings.SYSTEM_EVENT_TOKEN:
                    return {"id": 23}
                raise PermissionDenied({"status": "error", "message": "you don't have permission to access"})
            if 'HTTP_AUTHORIZATION' not in request.META or "platform_id" not in request.GET:
                raise PermissionDenied({"status": "error", "message": "you don't have permission to access"})
            token = request.META["HTTP_AUTHORIZATION"]
        try:
            response = requests.get(f"{self.url}api/check-platform/?platform_id={request.GET['platform_id']}",
                                    headers={"executetoken": token})
        except requests.ConnectionError:
            raise PermissionDenied({"status": "error", "message": "Authorization failed."})

        if response.status_code != 200:
            raise PermissionDenied({"status": "error", "message": "Authorization failed."})

        return response.json()["auth_info"]

    # method for dashboard app
    def get_check_dash_auth(self, request, *args, **kwargs):
        if 'HTTP_EXECUTETOKEN' not in request.META:
            raise PermissionDenied({"status": "error", "message": "you don't have permission to access"})
        auth_info = requests.post(f"{self.url}api/check-auth/",
                                  headers={"executetoken": request.META['HTTP_EXECUTETOKEN']}).json()
        if "is_admin" not in auth_info:
            raise PermissionDenied({"status": "error", "message": "Invalid dash user."})

        return auth_info["is_admin"]

    def get_check_admin(self, request, *args, **kwargs):
        user_info = self.get_user_info(request, *args, **kwargs)
        user_id = user_info["id"]
        if user_id in (19, 22, 23, 55):
            return user_id
        return False

    def get_credential(self, request, model):
        user_info = self.get_user_info(request)
        user_id = user_info["id"]
        # user_id = 16
        cred_id = request.GET.get("credential_id")

        credential = model.objects.filter(
            user_id=user_id,
            id=cred_id
        ).first()

        if not credential:
            raise PermissionDenied({"status": "error", "message": "Credential does not exist."})

        return credential
