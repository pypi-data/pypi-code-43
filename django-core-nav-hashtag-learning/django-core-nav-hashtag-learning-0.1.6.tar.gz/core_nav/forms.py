from django.forms import ModelForm

from schools.models import School, Authority, SCHOOL_TYPE
from users.models import User
from django import forms


class UserDetailsForm(ModelForm):

    class Meta:
        model = User

        fields = ['first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super(UserDetailsForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if len(first_name) == 0:
            raise forms.ValidationError('Please enter a first name')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if len(last_name) == 0:
            raise forms.ValidationError('Please enter a last name')
        return last_name

class SchoolDetailsForm(ModelForm):

    class Meta:
        model = School

        fields = ['school_name', 'authority', 'school_type']

    def __init__(self, *args, **kwargs):
        super(SchoolDetailsForm, self).__init__(*args, **kwargs)
        self.fields['school_name'].widget.attrs['class'] = 'form-control'
        self.fields['school_name'].widget.attrs['placeholder'] = 'School name'

        self.fields['authority'].label = 'Local authority'
        self.fields['authority'].widget.attrs['class'] = 'form-control'
        self.fields['authority'].queryset=Authority.objects.get_all_authorities()
        self.fields['authority'].empty_label = 'No local authority'

        self.fields['school_type'].label = 'School type'
        self.fields['school_type'].widget.attrs['class'] = 'form-control'
        self.fields['school_type'].choices=SCHOOL_TYPE

    def clean_school_name(self):
        return self.cleaned_data.get('school_name')

    def clean_authority(self):
        return self.cleaned_data.get('authority')

    def clean_school_type(self):
        return self.cleaned_data.get('school_type')



class ShowHelpForm(forms.Form):
    dont_show_help = forms.BooleanField(required=False)

    def set_initial(self):
        self.fields['dont_show_help'].initial = False

    def clean_dont_show_help(self):
        return self.cleaned_data.get('dont_show_help')

