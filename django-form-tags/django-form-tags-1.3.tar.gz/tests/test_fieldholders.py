from django.forms import forms
from django.test.testcases import SimpleTestCase
from django.utils.safestring import mark_safe

from form_tags.templatetags.forms import (
    fieldholder, fieldholder_combined, fieldholder_inline
)

from .mixins import DummyFormMixin, SvgIconsMixin


class FormFieldholderTestCase(DummyFormMixin, SvgIconsMixin, SimpleTestCase):
    maxDiff = None

    def test_fieldholder(self):
        html_output = fieldholder(
            {},
            self.form['char_field']
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput ">
                    <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" />
                </div>
            </div>
        ''')  # NOQA

    def test_fieldholder_fieldwrapper(self):
        html_output = fieldholder(
            {},
            self.form['char_field'],
            fieldwrapper_class="   test-class   "
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput test-class">
                    <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" />
                </div>
            </div>
        ''')  # NOQA

    def test_fieldholder_label(self):
        html_output = fieldholder(
            {},
            self.form['char_field'],
            label='Input field'
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Input field">Input field</label>
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput ">
                    <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" />
                </div>
            </div>
        ''')  # NOQA

        html_output = fieldholder(
            {},
            self.form['char_field'],
            label_tag=''
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput ">
                    <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" />
                </div>
            </div>
        ''')  # NOQA

        html_output = fieldholder(
            {},
            self.form['char_field'],
            label=mark_safe('<strong>Char field</strong>')
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field"><strong>Char field</strong></label>
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput ">
                    <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" />
                </div>
            </div>
        ''')  # NOQA

    def test_fieldholder_class(self):
        html_output = fieldholder(
            {},
            self.form['char_field'],
            fieldholder_class='  test-class  '
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder test-class">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput ">
                    <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" />
                </div>
            </div>
        ''')  # NOQA

    def test_context(self):
        html_output = fieldholder(
            {'horizontal': True},
            self.form['char_field']
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder fieldholder--horizontal">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput ">
                    <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" />
                </div>
            </div>
        ''')  # NOQA

        self.form.add_error('char_field', forms.ValidationError('Err'))
        html_output = fieldholder(
            {},
            self.form['char_field']
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder error">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput error">
                    <input class="error input-field" id="id_char_field" name="char_field" type="text" value="abc" />
                    <ul class="errorlist"><li>Err</li></ul>
                </div>
            </div>
        ''')  # NOQA

        html_output = fieldholder(
            {'suppress_errors': True},
            self.form['char_field']
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput ">
                    <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" />
                </div>
            </div>
        ''')  # NOQA

    def test_errors(self):
        self.form.add_error('char_field', forms.ValidationError('Err'))

        html_output = fieldholder(
            {},
            self.form['char_field']
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder error">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput error">
                    <input class="error input-field" id="id_char_field" name="char_field" type="text" value="abc" />
                    <ul class="errorlist"><li>Err</li></ul>
                </div>
            </div>
        ''')  # NOQA

        html_output = fieldholder(
            {},
            self.form['char_field'],
            suppress_errors=True
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput ">
                    <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" />
                </div>
            </div>
        ''')  # NOQA

    def test_fieldholder_help_text(self):
        help_field = fieldholder(
            {},
            self.form['help_field']
        )
        self.assertHTMLEqual(help_field, '''
            <div class="fieldholder ">
                <label for="id_help_field" title="Help field">Help field:</label>
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput ">
                    <input class="input-field" id="id_help_field" name="help_field" type="text" value="abc" />
                    <div class="helptext">Help Text</div>
                </div>
            </div>
        ''')  # NOQA

    def test_fieldholder_integer(self):
        html_output = fieldholder(
            {},
            self.form['int_field']
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_int_field" title="Int field">Int field:</label>
                <div class="fieldwrapper fieldwrapper--integerfield fieldwrapper--numberinput ">
                    <input class="input-field" id="id_int_field" name="int_field" type="number" value="1" />
                </div>
            </div>
        ''')  # NOQA

    def test_fieldholder_radio(self):
        html_output = fieldholder(
            {},
            self.form['radio_field']
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_radio_field_0" title="Radio field">Radio field:</label>
                <div class="fieldwrapper fieldwrapper--choicefield fieldwrapper--radioselect ">
                    <ul id="id_radio_field">
                        <li><label for="id_radio_field_0"><input checked="checked" class="" id="id_radio_field_0" name="radio_field" type="radio" value="1"> a</label></li>
                        <li><label for="id_radio_field_1"><input class="" id="id_radio_field_1" name="radio_field" type="radio" value="2"> b</label></li>
                    </ul>
                </div>
            </div>
        ''')  # NOQA

    def test_fieldholder_checkbox(self):
        html_output = fieldholder(
            {},
            self.form['checkbox_field']
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_checkbox_field" title="Checkbox field">Checkbox field:</label>
                <div class="fieldwrapper fieldwrapper--booleanfield fieldwrapper--checkboxinput ">
                    <label class="control checkbox">
                        <input checked class="" id="id_checkbox_field" name="checkbox_field" type="checkbox" />
                        <span class="control-indicator"></span>
                        <span class="control-label">Checkbox field</span>
                    </label>
                </div>
            </div>
        ''')  # NOQA

    def test_fieldholder_date(self):
        html_output = fieldholder(
            {},
            self.form['date_field']
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_date_field" title="Date field">Date field:</label>
                <div class="fieldwrapper fieldwrapper--datefield fieldwrapper--dateinput fieldwrapper--icon">
                    <input class="input-field" id="id_date_field" name="date_field" type="text" value="1940-10-9" />
                    <label class="label--inline-edit" for="id_date_field" title="Edit Date field">{}</label>
                </div>
            </div>
        '''.format(self.date_range_svg))  # NOQA

    def test_fieldholder_select(self):
        html_output = fieldholder(
            {},
            self.form['choice_field']
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_choice_field" title="Choice field">Choice field:</label>
                <div class="fieldwrapper fieldwrapper--choicefield fieldwrapper--select ">
                    <div class="select">
                        <select class="" id="id_choice_field" name="choice_field">
                            <option value="1" selected="selected">a</option>
                            <option value="2">b</option>
                        </select>
                    </div>
                </div>
            </div>
        ''')  # NOQA

    def test_fieldholder_password(self):
        html_output = fieldholder(
            {},
            self.form['pass_field']
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_pass_field" title="Pass field">Pass field:</label>
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--passwordinput fieldwrapper--icon">
                    <input class="input-field" id="id_pass_field" name="pass_field" type="password" />
                    <button class="input-icon input-icon__password" type="button" tabindex="-1">{}</button>
                </div>
            </div>
        '''.format(self.eye_svg))  # NOQA

    def test_fieldholder_textarea(self):
        html_output = fieldholder(
            {},
            self.form['text_field']
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_text_field" title="Text field">Text field:</label>
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textarea ">
                    <textarea class="" cols="40" id="id_text_field" name="text_field" rows="10">abc</textarea>
                </div>
            </div>
        ''')  # NOQA

    def test_fieldholder_field_kwargs(self):
        html_output = fieldholder(
            {},
            self.form['char_field'],
            **{
                'class': ' test class  ',
                'data_some': 'data',
                'placeholder': 'Fill in some test data'
            }
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput ">
                   <input class="input-field test class" data-some="data" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Fill in some test data" />
                </div>
            </div>
        ''')  # noqa

    def test_fieldholder_before_after_field(self):
        html_output = fieldholder(
            {},
            self.form['char_field'],
            after_field='@',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput ">
                    <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" />@
                </div>
            </div>
        ''')  # noqa

        html_output = fieldholder(
            {},
            self.form['char_field'],
            before_field='!',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput ">
                    !<input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" />
                </div>
            </div>
        ''')  # noqa

        html_output = fieldholder(
            {},
            self.form['char_field'],
            before_field='!',
            after_field='@',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput ">
                    !<input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" />@
                </div>
            </div>
        ''')  # noqa

        html_output = fieldholder(
            {},
            self.form['pass_field'],
            before_field='!',
            after_field='@',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_pass_field" title="Pass field">Pass field:</label>
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--passwordinput fieldwrapper--icon">
                    !<input class="input-field" id="id_pass_field" name="pass_field" type="password" />
                    <button class="input-icon input-icon__password" type="button" tabindex="-1">{}</button>
                </div>
            </div>
        '''.format(self.eye_svg))  # noqa

    def test_fieldholder_unit_text_left_right(self):
        html_output = fieldholder(
            {},
            self.form['char_field'],
            unit_text_left='$',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput fieldwrapper--unit">
                   <i class="input-unit input-unit--left">$</i>
                   <input class="input-field input-field--unit-left" id="id_char_field" name="char_field" type="text" value="abc" />
                </div>
            </div>
        ''')  # noqa

        html_output = fieldholder(
            {},
            self.form['char_field'],
            unit_text_left='$',
            unit_text_right='KM',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput fieldwrapper--unit">
                   <i class="input-unit input-unit--left">$</i>
                   <input class="input-field input-field--unit-left input-field--unit-right" id="id_char_field" name="char_field" type="text" value="abc" />
                   <i class="input-unit input-unit--right">KM</i>
                </div>
            </div>
        ''')  # noqa

        html_output = fieldholder(
            {},
            self.form['pass_field'],
            unit_text_left='$',
            unit_text_right='KM',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_pass_field" title="Pass field">Pass field:</label>
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--passwordinput fieldwrapper--icon">
                    <input class="input-field" id="id_pass_field" name="pass_field" type="password" />
                    <button class="input-icon input-icon__password" type="button" tabindex="-1">{}</button>
                </div>
            </div>
        '''.format(self.eye_svg))  # noqa


class FormFieldholderInlineTestCase(
        DummyFormMixin, SvgIconsMixin, SimpleTestCase):
    maxDiff = None

    def test_fieldholder_inline(self):
        html_output = fieldholder_inline(
            {},
            self.form['char_field']
        )
        self.assertHTMLEqual(html_output, '''
            <td class="table__cell table__cell--inline-edit ">
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput fieldwrapper--inline-edit">
                    <input class="input-field input-field--inline-edit" id="id_char_field" name="char_field" placeholder="Char field" type="text" value="abc" />
                    <label class="label--inline-edit" for="id_char_field" title="Edit Char field">{}</label>
                </div>
            </td>
        '''.format(self.edit_svg))  # NOQA

    def test_fieldholder_inline_integer(self):
        html_output = fieldholder_inline(
            {}, self.form['int_field']
        )
        self.assertHTMLEqual(html_output, '''
            <td class="table__cell table__cell--inline-edit ">
                <div class="fieldwrapper fieldwrapper--integerfield fieldwrapper--numberinput fieldwrapper--inline-edit">
                    <input class="input-field input-field--inline-edit" id="id_int_field" name="int_field" placeholder="Int field" type="number" value="1" />
                    <label class="label--inline-edit" for="id_int_field" title="Edit Int field">{}</label>
                </div>
            </td>
        '''.format(self.edit_svg))  # NOQA

    def test_fieldholder_inline_checkbox(self):
        html_output = fieldholder_inline(
            {},
            self.form['checkbox_field']
        )
        self.assertHTMLEqual(html_output, '''
            <td class="table__cell table__cell--inline-edit ">
                <div class="fieldwrapper fieldwrapper--booleanfield fieldwrapper--checkboxinput ">
                    <label class="control checkbox">
                        <input checked="checked" class="" id="id_checkbox_field" name="checkbox_field" type="checkbox" />
                        <span class="control-indicator"></span>
                        <span class="control-label">Checkbox field</span>
                    </label>
                </div>
            </td>
        ''')  # NOQA

    def test_fieldholder_inline_date(self):
        html_output = fieldholder_inline(
            {},
            self.form['date_field']
        )
        self.assertHTMLEqual(html_output, '''
            <td class="table__cell table__cell--inline-edit ">
                <div class="fieldwrapper fieldwrapper--datefield fieldwrapper--dateinput fieldwrapper--icon fieldwrapper--inline-edit">
                   <input class="input-field input-field--inline-edit" id="id_date_field" name="date_field" placeholder="Date field" type="text" value="1940-10-9" />
                   <label class="label--inline-edit" for="id_date_field" title="Edit Date field">{}</label>
                </div>
            </td>
        '''.format(self.date_range_svg))  # NOQA

    def test_fieldholder_inline_select(self):
        html_output = fieldholder_inline(
            {},
            self.form['choice_field']
        )
        self.assertHTMLEqual(html_output, '''
            <td class="table__cell table__cell--inline-edit ">
                <div class="fieldwrapper fieldwrapper--choicefield fieldwrapper--select select--inline-edit">
                    <div class="select">
                        <select class="" id="id_choice_field" name="choice_field">
                            <option value="1" selected="selected">a</option>
                            <option value="2">b</option>
                        </select>
                    </div>
                </div>
            </td>
        ''')  # NOQA

    def test_fieldholder_inline_radio(self):
        html_output = fieldholder_inline(
            {},
            self.form['radio_field']
        )
        self.assertHTMLEqual(html_output, '''
            <td class="table__cell table__cell--inline-edit ">
                <div class="fieldwrapper fieldwrapper--choicefield fieldwrapper--radioselect select--inline-edit">
                    <ul id="id_radio_field">
                        <li><label for="id_radio_field_0"><input checked="checked" class="" id="id_radio_field_0" name="radio_field" type="radio" value="1"> a</label></li>
                        <li><label for="id_radio_field_1"><input class="" id="id_radio_field_1" name="radio_field" type="radio" value="2"> b</label></li>
                    </ul>
                </div>
            </td>
        ''')  # NOQA

    def test_fieldholder_inline_password(self):
        html_output = fieldholder_inline(
            {},
            self.form['pass_field']
        )
        self.assertHTMLEqual(html_output, '''
            <td class="table__cell table__cell--inline-edit ">
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--passwordinput fieldwrapper--icon fieldwrapper--inline-edit">
                    <input class="input-field input-field--inline-edit" id="id_pass_field" name="pass_field" placeholder="Pass field" type="password" />
                    <button class="input-icon input-icon__password" type="button" tabindex="-1">{}</button>
                </div>
            </td>
        '''.format(self.eye_svg))  # NOQA

    def test_fieldholder_inline_textarea(self):
        html_output = fieldholder_inline(
            {},
            self.form['text_field']
        )
        self.assertHTMLEqual(html_output, '''
            <td class="table__cell table__cell--inline-edit ">
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textarea ">
                    <textarea class="" cols="40" id="id_text_field" name="text_field" rows="10">abc</textarea>
                </div>
            </td>
        ''')  # NOQA

    def test_fieldholder_inline_help_text(self):
        help_field = fieldholder_inline(
            {},
            self.form['help_field']
        )
        self.assertHTMLEqual(help_field, '''
            <td class="table__cell table__cell--inline-edit ">
                <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput fieldwrapper--inline-edit">
                    <input class="input-field input-field--inline-edit" id="id_help_field" name="help_field" placeholder="Help field" type="text" value="abc" />
                    <label class="label--inline-edit" for="id_help_field" title="Edit Help field">{}</label>
                    <div class="helptext">Help Text</div>
                </div>
            </td>
        '''.format(self.edit_svg))  # NOQA


class FormFieldholderCombinedTestCase(
        DummyFormMixin, SvgIconsMixin, SimpleTestCase):
    maxDiff = None

    def test_fieldholder_combined(self):
        html_output = fieldholder_combined(
            {},
            self.form['char_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput ">
                           <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Char field" />
                        </div>
                    </div>
                </div>
            </div>
        ''')  # noqa

        html_output = fieldholder_combined(
            {},
            self.form['char_field'],
            self.form['int_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput ">
                           <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Char field" />
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                </div>
            </div>
        ''')  # noqa

    def test_fieldholder_combined_class(self):
        html_output = fieldholder_combined(
            {},
            self.form['char_field'],
            self.form['int_field'],
            fieldholder_class='  test class  ',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder test class">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput ">
                           <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Char field" />
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                </div>
            </div>
        ''')  # noqa

    def test_fieldholder_combined_fieldwrapper_class(self):
        html_output = fieldholder_combined(
            {},
            self.form['char_field'],
            self.form['int_field'],
            fieldwrapper_class='  test class  ',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper test class">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput ">
                           <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Char field" />
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                </div>
            </div>
        ''')  # noqa

    def test_fieldholder_combined_label(self):
        html_output = fieldholder_combined(
            {},
            self.form['char_field'],
            self.form['int_field'],
            label='Input field'
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Input field">Input field</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput ">
                           <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Char field" />
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                </div>
            </div>
        ''')  # NOQA

        html_output = fieldholder_combined(
            {},
            self.form['char_field'],
            self.form['int_field'],
            label_tag=''
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput ">
                           <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Char field" />
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                </div>
            </div>
        ''')  # NOQA

        html_output = fieldholder_combined(
            {},
            self.form['char_field'],
            self.form['int_field'],
            label=mark_safe('<strong>Char field</strong>')
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field"><strong>Char field</strong></label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput ">
                           <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Char field" />
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                </div>
            </div>
        ''')  # NOQA

    def test_fieldholder_combined_context(self):
        html_output = fieldholder_combined(
            {'horizontal': True},
            self.form['char_field'],
            self.form['int_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder fieldholder--horizontal">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput ">
                           <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Char field" />
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                </div>
            </div>
        ''')  # NOQA

        self.form.add_error('char_field', forms.ValidationError('Err'))
        html_output = fieldholder_combined(
            {},
            self.form['char_field'],
            self.form['int_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput error">
                           <input class="input-field error" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Char field" />
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                    <ul class="errorlist"><li>Err</li></ul>
                </div>
            </div>
        ''')  # NOQA

        html_output = fieldholder_combined(
            {'suppress_errors': True},
            self.form['char_field'],
            self.form['int_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput ">
                           <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Char field" />
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                </div>
            </div>
        ''')  # NOQA

    def test_fieldholder_combined_errors(self):
        self.form.add_error('char_field', forms.ValidationError('Err'))

        html_output = fieldholder_combined(
            {},
            self.form['char_field'],
            self.form['int_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput error">
                           <input class="input-field error" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Char field" />
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                    <ul class="errorlist"><li>Err</li></ul>
                </div>
            </div>
        ''')  # noqa

        self.form.add_error('int_field', forms.ValidationError('Err2'))

        html_output = fieldholder_combined(
            {},
            self.form['char_field'],
            self.form['int_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput error">
                           <input class="input-field error" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Char field" />
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput error">
                           <input class="input-field error" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                    <ul class="errorlist"><li>Err</li></ul>
                    <ul class="errorlist"><li>Err2</li></ul>
                </div>
            </div>
        ''')  # noqa

        html_output = fieldholder_combined(
            {},
            self.form['char_field'],
            self.form['int_field'],
            suppress_errors=True,
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput ">
                           <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Char field" />
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                </div>
            </div>
        ''')  # noqa

    def test_fieldholder_combined_help_text(self):
        html_output = fieldholder_combined(
            {},
            self.form['help_field'],
            self.form['int_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_help_field" title="Help field">Help field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput ">
                           <input class="input-field" id="id_help_field" name="help_field" type="text" value="abc" placeholder="Help field" />
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                    <div class="helptext">Help Text</div>
                </div>
            </div>
        ''')  # noqa

        html_output = fieldholder_combined(
            {},
            self.form['help_field'],
            self.form['help_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_help_field" title="Help field">Help field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput ">
                           <input class="input-field" id="id_help_field" name="help_field" type="text" value="abc" placeholder="Help field" />
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput ">
                           <input class="input-field" id="id_help_field" name="help_field" type="text" value="abc" placeholder="Help field" />
                        </div>
                    </div>
                    <div class="helptext">Help Text</div>
                    <div class="helptext">Help Text</div>
                </div>
            </div>
        ''')  # noqa

        self.form.add_error('help_field', forms.ValidationError('Err'))
        self.form.add_error('int_field', forms.ValidationError('Err2'))

        html_output = fieldholder_combined(
            {},
            self.form['help_field'],
            self.form['int_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_help_field" title="Help field">Help field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput error">
                           <input class="input-field error" id="id_help_field" name="help_field" type="text" value="abc" placeholder="Help field" />
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput error">
                           <input class="input-field error" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                    <div class="helptext">Help Text</div>
                    <ul class="errorlist"><li>Err</li></ul>
                    <ul class="errorlist"><li>Err2</li></ul>
                </div>
            </div>
        ''')  # noqa

    def test_fieldholder_combined_select(self):
        html_output = fieldholder_combined(
            {},
            self.form['choice_field'],
            self.form['int_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_choice_field" title="Choice field">Choice field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--choicefield fieldwrapper--select select">
                            <select class="" id="id_choice_field" name="choice_field"><option selected="selected" value="1">a</option><option value="2">b</option></select>
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                </div>
            </div>
        ''')  # noqa

    def test_fieldholder_combined_password(self):
        html_output = fieldholder_combined(
            {},
            self.form['pass_field'],
            self.form['int_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_pass_field" title="Pass field">Pass field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--passwordinput fieldwrapper--icon">
                            <input class="input-field" id="id_pass_field" name="pass_field" type="password" placeholder="Pass field" />
                            <button class="input-icon input-icon__password" type="button" tabindex="-1">{}</button>
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                </div>
            </div>
        '''.format(self.eye_svg))  # noqa

    def test_fieldholder_combined_date(self):
        html_output = fieldholder_combined(
            {},
            self.form['date_field'],
            self.form['int_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_date_field" title="Date field">Date field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--datefield fieldwrapper--dateinput fieldwrapper--icon">
                            <input class="input-field" id="id_date_field" name="date_field" type="text" value="1940-10-9" placeholder="Date field" />
                            <label class="label--inline-edit" for="id_date_field" title="Edit Date field">{}</label>
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                </div>
            </div>
        '''.format(self.date_range_svg))  # noqa

    def test_fieldholder_combined_field_kwargs(self):
        html_output = fieldholder_combined(
            {},
            self.form['char_field'],
            self.form['int_field'],
            field0_class=' test class  ',
            field0_data_some='data',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput ">
                           <input class="input-field test class" data-some="data" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Char field" />
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                </div>
            </div>
        ''')  # noqa

        html_output = fieldholder_combined(
            {},
            self.form['char_field'],
            self.form['int_field'],
            field1_class=' test class  ',
            field1_data_some='data',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput ">
                           <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Char field" />
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field test class" data-some="data" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                </div>
            </div>
        ''')  # noqa

        html_output = fieldholder_combined(
            {},
            self.form['char_field'],
            self.form['int_field'],
            field0_class=' test class  ',
            field0_data_some='data',
            field1_class='test',
            field1_data_other='{}',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput ">
                           <input class="input-field test class" data-some="data" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Char field" />
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field test" data-other="{}" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                </div>
            </div>
        ''')  # noqa

    def test_fieldholder_combined_field_placeholder(self):
        html_output = fieldholder_combined(
            {},
            self.form['char_field'],
            self.form['int_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput ">
                           <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Char field" />
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                </div>
            </div>
        ''')  # noqa

        html_output = fieldholder_combined(
            {},
            self.form['char_field'],
            self.form['int_field'],
            field0_placeholder='',
            field1_placeholder='',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput ">
                           <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" placeholder="" />
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="" />
                        </div>
                    </div>
                </div>
            </div>
        ''')  # noqa

        html_output = fieldholder_combined(
            {},
            self.form['char_field'],
            self.form['int_field'],
            field0_placeholder='Test',
            field1_placeholder='Other',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput ">
                           <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Test" />
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="Other" />
                        </div>
                    </div>
                </div>
            </div>
        ''')  # noqa

    def test_fieldholder_combined_before_after_field(self):
        html_output = fieldholder_combined(
            {},
            self.form['char_field'],
            self.form['int_field'],
            field0_before_field='!',
            field0_after_field='@',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput ">
                           !<input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Char field" />@
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                </div>
            </div>
        ''')  # noqa

        html_output = fieldholder_combined(
            {},
            self.form['char_field'],
            self.form['int_field'],
            field0_before_field='!',
            field0_after_field='@',
            field1_before_field='#',
            field1_after_field='$',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput ">
                           !<input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Char field" />@
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           #<input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />$
                        </div>
                    </div>
                </div>
            </div>
        ''')  # noqa

        html_output = fieldholder_combined(
            {},
            self.form['pass_field'],
            self.form['int_field'],
            field0_before_field='!',
            field0_after_field='@',  # ignored
            field1_before_field='#',
            field1_after_field='$',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_pass_field" title="Pass field">Pass field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--passwordinput fieldwrapper--icon">
                            !<input class="input-field" id="id_pass_field" name="pass_field" type="password" placeholder="Pass field" />
                            <button class="input-icon input-icon__password" type="button" tabindex="-1">{}</button>
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           #<input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />$
                        </div>
                    </div>
                </div>
            </div>
        '''.format(self.eye_svg))  # noqa

    def test_fieldholder_combined_unit_text_left_right(self):
        html_output = fieldholder_combined(
            {},
            self.form['char_field'],
            self.form['int_field'],
            field0_unit_text_left='$',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput fieldwrapper--unit">
                           <i class="input-unit input-unit--left">$</i>
                           <input class="input-field input-field--unit-left" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Char field" />
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                </div>
            </div>
        ''')  # noqa

        html_output = fieldholder_combined(
            {},
            self.form['char_field'],
            self.form['int_field'],
            field0_unit_text_left='$',
            field0_unit_text_right='KM',
            field1_unit_text_left=mark_safe('&euro;'),
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_char_field" title="Char field">Char field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput fieldwrapper--unit">
                           <i class="input-unit input-unit--left">$</i>
                           <input class="input-field input-field--unit-left input-field--unit-right" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Char field" />
                           <i class="input-unit input-unit--right">KM</i>
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput fieldwrapper--unit">
                           <i class="input-unit input-unit--left">&euro;</i>
                           <input class="input-field input-field--unit-left" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                </div>
            </div>
        ''')  # noqa

        html_output = fieldholder_combined(
            {},
            self.form['pass_field'],
            self.form['int_field'],
            field0_unit_text_left='$',
            field0_unit_text_right='KM',
            field1_unit_text_left=mark_safe('&euro;'),
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_pass_field" title="Pass field">Pass field:</label>
                <div class="fieldwrapper ">
                    <div class="fieldwrapper-combined">
                        <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--passwordinput fieldwrapper--icon">
                            <input class="input-field" id="id_pass_field" name="pass_field" type="password" placeholder="Pass field" />
                            <button class="input-icon input-icon__password" type="button" tabindex="-1">{}</button>
                        </div>
                        <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput fieldwrapper--unit">
                           <i class="input-unit input-unit--left">&euro;</i>
                           <input class="input-field input-field--unit-left" id="id_int_field" name="int_field" type="number" value="1" placeholder="Int field" />
                        </div>
                    </div>
                </div>
            </div>
        '''.format(self.eye_svg))  # noqa

    def test_fieldholder_combined_uses_widget_placeholders(self):
        html_output = fieldholder_combined(
            {},
            self.form['int_field'],
            self.form['int_field'],
            self.form['int_field'],
            field0_placeholder='Eerste',
            field1_placeholder='Tweede',
            field2_placeholder='Derde'
        )

        html = '''
            <div class="fieldholder ">
                <label for="id_int_field" title="Int field">Int field:</label>
               <div class="fieldwrapper ">
                   <div class="fieldwrapper-combined">
                       <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" placeholder="Eerste" type="number" value="1" />
                       </div>
                       <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" placeholder="Tweede" type="number" value="1" />
                       </div>
                       <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" placeholder="Derde" type="number" value="1" />
                       </div>
                   </div>
               </div>
           </div>
        '''  # noqa

        self.assertHTMLEqual(html_output, html)

        self.form.fields['int_field'].widget.attrs.update(
            placeholder='lorem ipsum')

        html_output = fieldholder_combined(
            {},
            self.form['int_field'],
            self.form['int_field'],
            self.form['int_field'],
            field0_placeholder='Eerste',
            field1_placeholder='Tweede',
            field2_placeholder='Derde'
        )

        self.assertHTMLEqual(html_output, html)

        html_output = fieldholder_combined(
            {},
            self.form['int_field'],
            self.form['int_field'],
            self.form['int_field'],
        )

        self.assertHTMLEqual(html_output, '''
            <div class="fieldholder ">
                <label for="id_int_field" title="Int field">Int field:</label>
               <div class="fieldwrapper ">
                   <div class="fieldwrapper-combined">
                       <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" placeholder="lorem ipsum" type="number" value="1" />
                       </div>
                       <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" placeholder="lorem ipsum" type="number" value="1" />
                       </div>
                       <div class="fieldwrapper-combined__field fieldwrapper--integerfield fieldwrapper--numberinput ">
                           <input class="input-field" id="id_int_field" name="int_field" placeholder="lorem ipsum" type="number" value="1" />
                       </div>
                   </div>
               </div>
           </div>
        ''')  # noqa
