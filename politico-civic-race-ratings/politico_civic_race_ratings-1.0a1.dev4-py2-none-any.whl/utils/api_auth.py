# Imports from Django.
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.utils.decorators import method_decorator


# Imports from other dependencies.
from rest_framework import authentication
from rest_framework import exceptions


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
