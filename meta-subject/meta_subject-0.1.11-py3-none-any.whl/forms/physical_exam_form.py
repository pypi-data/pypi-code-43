from edc_constants.constants import OTHER, NONE, NO, YES
from edc_form_validators import FormValidator

from .form_mixins import SubjectModelFormMixin
from ..models import PhysicalExam


class PhysicalExamFormValidator(FormValidator):
    def clean(self):

        self.required_if(
            YES, field="is_heartbeat_regular", field_required="irregular_heartbeat"
        )

        self.required_if(
            YES, field="has_abdominal_tenderness", field_required="abdominal_tenderness"
        )


class PhysicalExamForm(SubjectModelFormMixin):

    form_validator_cls = PhysicalExamFormValidator

    class Meta:
        model = PhysicalExam
        fields = "__all__"
