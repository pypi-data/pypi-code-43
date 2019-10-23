# Imports from Django.
from django.conf import settings
from django.utils.decorators import method_decorator


# Imports from race_ratings.
from raceratings.utils.importers import import_class


def secure(view):
    """
    Authentication decorator for views.

    If DEBUG is on, we serve the view without authenticating.
    Default is 'django.contrib.auth.decorators.login_required'.
    Can also be 'django.contrib.admin.views.decorators.staff_member_required'
    or a custom decorator.
    """
    auth_decorator = import_class(
        getattr(
            settings,
            "RACE_RATINGS_AUTH_DECORATOR",
            "django.contrib.auth.decorators.login_required",
        )
    )
    is_debug = getattr(settings, "DEBUG", False)

    return (
        view
        if is_debug
        else method_decorator(auth_decorator, name="dispatch")(view)
    )
