from edc_form_validators import FormValidator

from .form_mixins import SubjectModelFormMixin
from ..models import FollowupVitals


class FollowupFormValidator(FormValidator):
    pass


class FollowupVitalsForm(SubjectModelFormMixin):

    # form_validator_cls = FollowupFormValidator

    class Meta:
        model = FollowupVitals
        fields = "__all__"
