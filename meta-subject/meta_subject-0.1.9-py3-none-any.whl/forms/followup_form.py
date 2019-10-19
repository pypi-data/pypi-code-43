# from meta_form_validators import FollowupFormValidator

from .form_mixins import SubjectModelFormMixin
from ..models import Followup


class FollowupForm(SubjectModelFormMixin):

    # form_validator_cls = FollowupFormValidator

    class Meta:
        model = Followup
        fields = "__all__"
