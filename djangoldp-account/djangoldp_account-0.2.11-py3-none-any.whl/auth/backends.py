import json

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.validators import validate_email
from jwkest import BadSyntax
from jwkest.jwt import JWT

from djangoldp_account.auth.solid import Solid
from djangoldp_account.errors import LDPLoginError

UserModel = get_user_model()


class EmailOrUsernameAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            validate_email(username)
            user = UserModel.objects.get(email=username)
            if user.check_password(password):
                return user
        except (ValidationError, UserModel.DoesNotExist):
            return super().authenticate(request, username, password, **kwargs)


class ExternalUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if 'HTTP_AUTHORIZATION' in request.META:
            jwt = request.META['HTTP_AUTHORIZATION']
            if jwt.startswith("Bearer"):
                jwt = jwt[7:]
            _jwt = JWT()
            try:
                unpacked = json.loads(_jwt.unpack(jwt).part[1])
            except BadSyntax:
                return
            try:
                id_token = json.loads(_jwt.unpack(unpacked['id_token']).part[1])
            except KeyError:
                id_token = unpacked
            try:
                Solid.check_id_token_exp(id_token['exp'])
                Solid.confirm_webid(id_token['sub'], id_token['iss'])
            except LDPLoginError as e:
                raise PermissionDenied(e.description)
            userinfo = {
                'sub': id_token['sub']
            }
            user = Solid.get_or_create_user(userinfo, id_token['sub'])

            if self.user_can_authenticate(user):
                return user
