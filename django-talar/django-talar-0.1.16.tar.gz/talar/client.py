import jwt
from django.conf import settings

from .serializers import PaymentSerializer


class Talar:
    """
    Talar integration class. Used to perform actions for Talar API.
    """

    def __init__(self):
        self.project_id = settings.TALAR['project_id']

        self.access_key_id = settings.TALAR['access_key_id']
        self.access_key = settings.TALAR['access_key']

        self.url = f'https://talar.app/p/{self.project_id}/order/classic/create/'

    def create_payment_data(self, data: dict):
        talar_serializer = PaymentSerializer(data=data)
        talar_serializer.is_valid(raise_exception=True)

        encrypted_data = jwt.encode(
            talar_serializer.validated_data,
            self.access_key,
            algorithm='HS256',
            headers={'kid': self.access_key_id}
        )
        return encrypted_data.decode("utf-8")
