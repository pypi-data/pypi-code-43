from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .models import EmailModel


""" Start EmailForm here. """
# start emailform here.
class EmailForm(ModelForm):

    class Meta:
        model = EmailModel
        fields = ['email', 'full_name', 'content' ]
        labels = {'email': 'Email', 'full_name' : 'Full Name', 'content' : 'Message' }

        widgets = {'email' :  forms.EmailInput(attrs={"type": "email", "class": "form-control rounded-0", "placeholder": "Email address"}),
                   'full_name': forms.TextInput(attrs={"type":"text", "class": "form-control rounded-0", "placeholder": "Full name"}),
                   'content': forms.Textarea(attrs={"type": "text", "class": "form-control rounded-0", "placeholder": " Your message", "rows": "4"}) }