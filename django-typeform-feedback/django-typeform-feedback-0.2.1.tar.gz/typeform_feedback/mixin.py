from django.contrib.contenttypes.models import ContentType

from .models import GenericTypeformFeedback, UserGenericTypeformFeedback


class TypeformMixin:

    def get_surveys(self):
        instance_content_type = ContentType.objects.get_for_model(self)
        return GenericTypeformFeedback.objects.filter(
            object_id=self.pk,
            content_type=instance_content_type,
        )

    def get_answers(self, typeform_id):
        return UserGenericTypeformFeedback.objects.filter(
            feedback__typeform_id=typeform_id,
        )

    def get_user_answers(self, user, typeform_id):
        return self.get_answers(typeform_id).filter(
            user=user,
        )
