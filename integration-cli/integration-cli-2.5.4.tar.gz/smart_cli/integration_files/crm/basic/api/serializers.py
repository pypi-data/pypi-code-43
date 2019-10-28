from django.urls import reverse
from rest_framework import serializers
from .models import Credential
from .models import (
    CallReport
)

from config_field import ConfigSerializerMethodField


class CredentialSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Credential
        fields = (
            "id",
            "platform_id",
            "main_user",
            "user_id",
            "url",
            "login",
        )
        extra_kwargs = {
            "id": {"read_only": True},
        }

    def get_url(self, obj):
        request = self.context.get('request')

        return request.build_absolute_uri(reverse("credential-detail", kwargs={"pk": obj.id}))
