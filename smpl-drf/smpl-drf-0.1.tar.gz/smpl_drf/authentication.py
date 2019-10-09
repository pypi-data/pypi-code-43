
from rest_framework.authentication import SessionAuthentication


class SkipCSFRSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        pass
