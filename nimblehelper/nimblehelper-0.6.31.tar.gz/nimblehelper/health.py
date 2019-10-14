from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from django.contrib.auth.models import User


class HealthViewSet(GenericViewSet):
    """
    API that checks db status (checks server status if able to reach)
    """
    def list(self, request):
        status = "UP"
        try:
            if request.GET.get('status', None):
                status = "UP"
            self.__test_creating_user()
            db_status = "UP"
            status_code = 200
        except ConnectionError:
            db_status = "DOWN"
            status_code = 500
        health_data = {
            "dbStatus": db_status,
            "serviceStatus": status
        }
        return Response(health_data, status=status_code)

    @staticmethod
    def __test_creating_user():
        test_db_user = User.objects.create(username="FooBar")
        test_db_user.save()
        test_db_user.delete()
