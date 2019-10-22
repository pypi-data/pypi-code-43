from django.conf import settings
from django.views.generic.detail import DetailView

from ..models import UserGenericTypeformFeedback


class ActionUserTypeformView(DetailView):
    model = UserGenericTypeformFeedback
    template_name = settings.TYPEFORM_FEEDBACK_TEMPLATE_USER_VALIDATION
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'


class ValidateUserTypeformView(ActionUserTypeformView):

    def get(self, request, *args, **kwargs):
        self.get_object().mark_as_approved()
        return super().get(request, *args, **kwargs)


class InvalidateUserTypeformView(ActionUserTypeformView):

    def get(self, request, *args, **kwargs):
        self.get_object().mark_as_fail()
        return super().get(request, *args, **kwargs)
