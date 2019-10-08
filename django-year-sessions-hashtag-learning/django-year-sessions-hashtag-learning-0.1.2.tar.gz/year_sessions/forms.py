from django import forms

from year_sessions.models import YearSession


class ChangeSessionForm(forms.Form):
    session_field = forms.ModelChoiceField(
        queryset=YearSession.objects.get_year_sessions_excluding_those_passed(),
        label='Session'
    )

    def __init__(self, *args, **kwargs):
        super(ChangeSessionForm, self).__init__(*args, **kwargs)

        self.fields['session_field'].empty_label = 'Select session...'
        self.fields['session_field'].widget.attrs['class'] = 'form-control'