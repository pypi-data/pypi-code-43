from rest_framework.authentication import BaseAuthentication, BasicAuthentication as RestBasicAuthentication


class SessionAuthentication(BaseAuthentication):

    def authenticate(self, request):
        user = getattr(request._request, 'user', None)
        if not user or not user.is_active:
            return None
        return (user, None)


class BasicAuthentication(RestBasicAuthentication):
    pass
