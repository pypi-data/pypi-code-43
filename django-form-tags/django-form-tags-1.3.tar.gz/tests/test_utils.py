import django
from django import forms
from django.forms.formsets import formset_factory
from django.test.testcases import SimpleTestCase

from form_tags.templatetags.forms import (
    _add_error_class, _get_field_kwargs, _help_text, _unit_text, hidden_fields,
    non_field_errors, non_form_errors
)

from .mixins import DummyForm, DummyFormMixin, DummyFormSet


class UtilsTestCase(DummyFormMixin, SimpleTestCase):
    maxDiff = None

    def test_add_error_class(self):
        assert _add_error_class(None, self.form['char_field'], False) == ''
        assert _add_error_class('', self.form['char_field'], False) == ''
        assert _add_error_class('test', self.form['char_field'], False) == 'test'  # noqa
        assert _add_error_class('test multiple', self.form['char_field'], False) == 'test multiple'  # noqa
        assert _add_error_class(' test multiple  ', self.form['char_field'], False) == 'test multiple'  # noqa

        self.form.add_error('char_field', forms.ValidationError('Err'))

        assert _add_error_class(None, self.form['char_field'], False) == 'error'  # noqa
        assert _add_error_class('', self.form['char_field'], False) == 'error'
        assert _add_error_class('test', self.form['char_field'], False) == 'test error'  # noqa
        assert _add_error_class('test multiple', self.form['char_field'], False) == 'test multiple error'  # noqa
        assert _add_error_class(' test multiple  ', self.form['char_field'], False) == 'test multiple error'  # noqa

        assert _add_error_class(None, self.form['char_field'], True) == ''
        assert _add_error_class('', self.form['char_field'], True) == ''
        assert _add_error_class('test', self.form['char_field'], True) == 'test'  # noqa
        assert _add_error_class('test multiple', self.form['char_field'], True) == 'test multiple'  # noqa
        assert _add_error_class(' test multiple  ', self.form['char_field'], True) == 'test multiple'  # noqa

    def test_help_text(self):
        assert _help_text(None) == ''
        assert _help_text('') == ''
        assert _help_text('Help me!') == '<div class="helptext">Help me!</div>'

    def test_get_field_kwargs(self):
        kwargs = {
            'some_arg': 'test',
            'field0_class': '',
            'field1_class': 'test',
            'field1_data_some': '',
        }
        assert _get_field_kwargs(0, **kwargs) == {
            'class': ''
        }
        assert _get_field_kwargs(1, **kwargs) == {
            'class': 'test',
            'data_some': '',
        }
        assert _get_field_kwargs(3, **kwargs) == {}
        assert _get_field_kwargs(0) == {}

    def test_unit_text(self):
        assert _unit_text(None, None) == {}
        assert _unit_text('', '') == {}
        assert _unit_text('$', '') == {
            'fieldwrapper_class': 'fieldwrapper--unit',
            'before_field': '<i class="input-unit input-unit--left">$</i>\n'
        }
        assert _unit_text('', 'KM') == {
            'fieldwrapper_class': 'fieldwrapper--unit',
            'after_field': '<i class="input-unit input-unit--right">KM</i>\n'
        }
        assert _unit_text('&', 'KM') == {
            'fieldwrapper_class': 'fieldwrapper--unit',
            'before_field':
                '<i class="input-unit input-unit--left">&amp;</i>\n',
            'after_field': '<i class="input-unit input-unit--right">KM</i>\n'
        }
        assert _unit_text('&', 'KM', 'fieldwrapper--icon') == {}
        assert _unit_text('&', 'KM', '  other-class  ') == {
            'fieldwrapper_class': 'fieldwrapper--unit other-class',
            'before_field':
                '<i class="input-unit input-unit--left">&amp;</i>\n',
            'after_field': '<i class="input-unit input-unit--right">KM</i>\n'
        }

    def test_hidden_fields(self):
        html_output = hidden_fields(self.form)
        self.assertHTMLEqual(html_output, '''
            <input id="id_hidden_field" name="hidden_field" type="hidden" />
            <input id="id_another_hidden_field" name="another_hidden_field" type="hidden" />
        ''')  # noqa

    def test_non_field_errors(self):
        html_output = non_field_errors(self.form)
        assert html_output == ''

        self.form.add_error(None, forms.ValidationError('test'))
        html_output = non_field_errors(self.form)

        if django.VERSION >= (1, 8, 0):
            self.assertHTMLEqual(html_output, '''
                <div class="inline-validation inline-validation--error">
                   <ul class="errorlist nonfield"><li>test</li></ul>
                </div>
            ''')
        else:
            self.assertHTMLEqual(html_output, '''
                <div class="inline-validation inline-validation--error">
                   <ul class="errorlist"><li>test</li></ul>
                </div>
            ''')

    def test_non_form_errors(self):
        formset = formset_factory(DummyForm, DummyFormSet)
        dummy_formset = formset()
        html_output = non_form_errors(dummy_formset)
        assert html_output == ''

        dummy_formset.add_error()
        html_output = non_form_errors(dummy_formset)
        self.assertHTMLEqual(html_output, '''
            <div class="inline-validation inline-validation--error">
               <ul class="errorlist"><li>Non form error 2</li></ul>
            </div>
        ''')
