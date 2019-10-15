from django import forms
from svg_templatetag.templatetags.svg import get_svg


class DummyFormSet(forms.BaseFormSet):
    def add_error(self):
        self._non_form_errors = self.error_class(
            forms.ValidationError("Non form error 2").error_list)


class DummyForm(forms.Form):
    use_required_attribute = False
    char_field = forms.CharField()
    int_field = forms.IntegerField()
    date_field = forms.DateField()
    checkbox_field = forms.BooleanField()
    checkbox_help_field = forms.BooleanField(help_text='Help Me!')
    text_field = forms.CharField(widget=forms.Textarea)
    pass_field = forms.CharField(widget=forms.PasswordInput)
    choice_field = forms.ChoiceField(choices=[('1', 'a'), ('2', 'b')])
    radio_field = forms.ChoiceField(
        widget=forms.RadioSelect, choices=[('1', 'a'), ('2', 'b')])
    help_field = forms.CharField(help_text='Help Text')
    hidden_field = forms.CharField(widget=forms.HiddenInput)
    another_hidden_field = forms.Field(widget=forms.HiddenInput)


class DummyFormMixin(object):
    def setUp(self):
        self.form = DummyForm({
            'char_field': 'abc',
            'int_field': 1,
            'date_field': '1940-10-9',
            'text_field': 'abc',
            'checkbox_field': True,
            'checkbox_help_field': True,
            'pass_field': 'secret',
            'choice_field': '1',
            'radio_field': '1',
            'help_field': 'abc',
        })


class SvgIconsMixin(object):
    @classmethod
    def setUpClass(cls):
        super(SvgIconsMixin, cls).setUpClass()
        cls.eye_svg = get_svg(
            'form_tags/icon_eye.svg',
            **{'class': 'icn icn--ic-24 icn--ic-remove-red-eye'})

        cls.edit_svg = get_svg(
            'form_tags/icon_edit.svg',
            **{'class': 'icn icn--ic-24 icn--ic-edit'})

        cls.date_range_svg = get_svg(
            'form_tags/icon_date_range.svg',
            **{'class': 'icn icn--ic-24 icn--ic-date-range'})
