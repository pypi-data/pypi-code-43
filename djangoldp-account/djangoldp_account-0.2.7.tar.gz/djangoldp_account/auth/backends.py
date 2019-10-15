import json

from django.contrib.auth.backends import ModelBackend, UserModel
from django.core.exceptions import PermissionDenied
from jwkest import BadSyntax
from jwkest.jwt import JWT

from djangoldp_account.auth.solid import Solid
from djangoldp_account.errors import LDPLoginError


class ExternalUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):

        user = None
        if 'HTTP_AUTHORIZATION' in request.META:
            jwt = request.META['HTTP_AUTHORIZATION']
            if jwt.startswith("Bearer"):
                jwt = jwt[7:]
            username = kwargs.get(UserModel.USERNAME_FIELD)
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

