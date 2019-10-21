from django.conf import settings

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..models import UserGenericTypeformFeedback


class UserResponseValidationSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserGenericTypeformFeedback
        fields = []

    def validate(self, data):
        user_response = self.Meta.model.objects.get(uuid=self.initial_data.get('uuid'))
        valid_statuses = [
            settings.TYPEFORM_FEEDBACK_USER_FEEDBACK_STATUS_ANSWERED,
            settings.TYPEFORM_FEEDBACK_USER_FEEDBACK_STATUS_FAIL,
        ]

        try:
            assert user_response.status in valid_statuses
        except AssertionError:
            raise ValidationError('This uuid is not valid')

        return data


class UserResponseOKSerializer(UserResponseValidationSerializer):

    def update(self, instance, validated_data):
        instance.mark_as_approved()


class UserResponseKOSerializer(UserResponseValidationSerializer):

    def update(self, instance, validated_data):
        instance.mark_as_fail()
