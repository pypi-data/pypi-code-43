from django import forms
from django.test.testcases import SimpleTestCase

from form_tags.templatetags.forms import field_tag

from .mixins import DummyFormMixin


class FormFieldTestCase(DummyFormMixin, SimpleTestCase):
    maxDiff = None

    def test_field_attributes(self):
        html_output = field_tag(self.form['char_field'], **{
            'class': 'test-class awesome',
            'any': 'attr'
        })
        self.assertHTMLEqual(html_output, '''
            <input class="input-field test-class awesome" any="attr" id="id_char_field" name="char_field" type="text" value="abc" />
        ''')  # noqa

        html_output = field_tag(self.form['text_field'], **{
            'class': 'test-class awesome',
            'any': 'attr'
        })
        self.assertHTMLEqual(html_output, '''
            <textarea class="test-class awesome" any="attr" cols="40" id="id_text_field" name="text_field" rows="10">abc</textarea>
        ''')  # noqa

        html_output = field_tag(self.form['char_field'])
        self.assertHTMLEqual(html_output, '''
            <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" />
        ''')  # noqa

    def test_field_text_input(self):
        html_output = field_tag(self.form['char_field'])
        self.assertHTMLEqual(html_output, '''
            <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" />
        ''')  # noqa

        html_output = field_tag(self.form['text_field'])
        self.assertHTMLEqual(html_output, '''
            <textarea class="" cols="40" id="id_text_field" name="text_field" rows="10">abc</textarea>
        ''')  # noqa

        self.form['char_field'].field.widget.attrs.update({'class': 'test'})
        self.form['text_field'].field.widget.attrs.update({'class': 'test'})

        html_output = field_tag(self.form['char_field'])
        self.assertHTMLEqual(html_output, '''
            <input class="input-field test" id="id_char_field" name="char_field" type="text" value="abc" />
        ''')  # noqa

        html_output = field_tag(self.form['text_field'])
        self.assertHTMLEqual(html_output, '''
            <textarea class="test" cols="40" id="id_text_field" name="text_field" rows="10">abc</textarea>
        ''')  # noqa

    def test_field_boolean_attrs(self):
        html_output = field_tag(self.form['char_field'], **{
            'autofocus': True,
            'checked': 1,
            'disabled': 'yes',
            'formnovalidate': 'formnovalidate',
            'multiple': '1',
            'readonly': '1',
            'required': '1',
        })
        self.assertHTMLEqual(html_output, '''
            <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" autofocus="autofocus" checked="checked" disabled="disabled" formnovalidate="formnovalidate" multiple="multiple" readonly="readonly" required="required" />
        ''')  # noqa

        html_output = field_tag(self.form['char_field'], **{
            'autofocus': False,
            'checked': 0,
            'disabled': '',
        })
        self.assertHTMLEqual(html_output, '''
            <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" />
        ''')  # noqa

        with self.settings(FIELD_BOOLEAN_ATTRS=['test']):
            html_output = field_tag(self.form['char_field'], **{
                'autofocus': '1',
                'checked': '2',
                'disabled': '3',
                'formnovalidate': '4',
                'multiple': '5',
                'readonly': '6',
                'required': '7',
                'test': '8'
            })
            self.assertHTMLEqual(html_output, '''
                <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" autofocus="1" checked="2" disabled="3" formnovalidate="4" multiple="5" readonly="6" required="7" test="test" />
            ''')  # noqa

    def test_field_suppress_errors(self):
        self.form.add_error('char_field', forms.ValidationError('Err'))

        html_output = field_tag(self.form['char_field'], suppress_errors=True)
        self.assertHTMLEqual(html_output, '''
            <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" />
        ''')  # noqa

        html_output = field_tag(self.form['char_field'], suppress_errors=False)
        self.assertHTMLEqual(html_output, '''
            <input class="input-field error" id="id_char_field" name="char_field" type="text" value="abc" />
        ''')  # noqa

        html_output = field_tag(self.form['char_field'])
        self.assertHTMLEqual(html_output, '''
            <input class="input-field error" id="id_char_field" name="char_field" type="text" value="abc" />
        ''')  # noqa

    def test_field_name(self):
        html_output = field_tag(self.form['char_field'], **{
            'name': "custom-field-name",
        })
        self.assertHTMLEqual(html_output, '''
            <input class="input-field" id="id_char_field" name="custom-field-name" type="text" value="abc" />
        ''')
