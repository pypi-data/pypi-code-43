from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_visit_tracking.modelform_mixins import SubjectModelFormMixin
from meta_form_validators.form_validators import BloodResultsHba1cFormValidator

from ...models import BloodResultsHba1c


class BloodResultsHba1cForm(
    ActionItemFormMixin, SubjectModelFormMixin, forms.ModelForm
):

    form_validator_cls = BloodResultsHba1cFormValidator

    class Meta:
        model = BloodResultsHba1c
        fields = "__all__"
