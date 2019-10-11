from django import forms
from django.utils.translation import gettext as _

from captcha.fields import ReCaptchaField

from .models import ContactRequest


class ContactRequestForm(forms.ModelForm):
    captcha = ReCaptchaField(label='')

    class Meta:
        model = ContactRequest
        fields = [
            'name',
            'email',
            'phone_number',
            'message'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False
        self.fields['phone_number'].required = False

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get('email') and not cleaned_data.get('phone_number'):
            raise forms.ValidationError(_("Email or phone number are required."))

        return cleaned_data
