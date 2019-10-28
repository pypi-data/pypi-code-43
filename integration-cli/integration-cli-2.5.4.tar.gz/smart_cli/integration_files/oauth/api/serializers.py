from django.urls import reverse
from rest_framework import serializers
from .models import Credential


class CredentialSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Credential
        fields = [
            "id",
            "login",
            "client_service_id",
            "platform_id",
            "main_user",
            "user_id",
            "access_token",
            "refresh_token",
            "expires_in",
            "url",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "access_token": {"write_only": True},
            "refresh_token": {"write_only": True},
        }

    def get_url(self, obj):
        request = self.context.get('request')

        return request.build_absolute_uri(reverse("credential-detail", kwargs={"pk": obj.id}))
