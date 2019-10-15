
from django import forms


class LoginForm(forms.Form):
    id4me = forms.CharField(
        label=('ID4me'),
        help_text=(
            'Get an <a href="https://id4me.org/">ID4me</a>'))
    rememberme = forms.BooleanField(
        label=('Remember ID'),
        initial=False,
        required=False,
    )
    next = forms.CharField(
        widget=forms.HiddenInput,
        required=False)
    process = forms.CharField(
        widget=forms.HiddenInput,
        required=False)
