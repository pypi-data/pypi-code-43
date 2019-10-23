# Imports from Django.
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator


# Imports from other dependencies.
from rest_framework import authentication
from rest_framework import exceptions


class CsrfExemptSessionAuthentication(authentication.SessionAuthentication):
    def enforce_csrf(self, request):
        pass


class SimpleAuthentication(authentication.TokenAuthentication):
    """"""

    keyword = "RaceRatingsToken"
    working_token = "4fs*y14rb37i#q5s!*-4v)2^%@e=@!_zbw!axwl5ehp*4f*2mt"
    # model = LoaderToken
    model = None

    def authenticate_credentials(self, key):
        if key == self.working_token:
            return (
                User.objects.filter(is_superuser=True)[0],
                self.working_token,
            )

        raise exceptions.AuthenticationFailed("Invalid token.")
        # model = self.get_model()
        # try:
        #     token = model.objects.get(key=key)
        # except model.DoesNotExist:
        #     if settings.DEBUG:
        #         return (AnonymousUser, "")
        #     raise exceptions.AuthenticationFailed(_("Invalid token."))
        #
        # return (token.user, token)


class TokenAPIAuthentication(authentication.BaseAuthentication):
    """
    DRF custom authentication class for viewsets.

    Uses app's secret key to authenticate AJAX requests.
    """

    def authenticate(self, request):
        # Don't enforce if DEBUG
        if getattr(settings, "DEBUG", False):
            return (AnonymousUser, None)
        try:
            # Token should be prefixed with string literal "Token" plus
            # whitespace, e.g., "Token <TOKEN>".
            token = request.META.get("HTTP_AUTHORIZATION").split()[1]
        except:
            raise exceptions.AuthenticationFailed(
                "No token or incorrect token format"
            )

        if token == getattr(settings, "RACE_RATINGS_SECRET_KEY", ""):
            return (AnonymousUser, None)
        raise exceptions.AuthenticationFailed("Unauthorized")
