from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_visit_tracking.modelform_mixins import SubjectModelFormMixin
from meta_form_validators.form_validators import BloodResultsGluFormValidator

from ...models import BloodResultsGlu


class BloodResultsGluForm(ActionItemFormMixin, SubjectModelFormMixin, forms.ModelForm):

    form_validator_cls = BloodResultsGluFormValidator

    class Meta:
        model = BloodResultsGlu
        fields = "__all__"
