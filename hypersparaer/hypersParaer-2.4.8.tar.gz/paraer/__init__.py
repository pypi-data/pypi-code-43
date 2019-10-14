__version__ = "2.4.8"


from rest_framework.authentication import SessionAuthentication

from .datastrctures import MethodProxy, Result, Valid
from .doc import patch_all
from .para import para_ok_or_400, perm_ok_or_403

__all__ = ("Result", "MethodProxy", "Valid", "para_ok_or_400", "perm_ok_or_403")
patch_all()


def authenticate_header(self, request):
    return True


SessionAuthentication.authenticate_header = authenticate_header
