from django import forms
from django.test.testcases import SimpleTestCase
from django.utils.safestring import mark_safe

from form_tags.templatetags.forms import fieldwrapper, fieldwrapper_combined

from .mixins import DummyFormMixin, SvgIconsMixin


class FormFieldwrapperTestCase(DummyFormMixin, SvgIconsMixin, SimpleTestCase):
    maxDiff = None

    def test_fieldwrapper(self):
        html_output = fieldwrapper(
            self.form['char_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput ">
                <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" />
            </div>
        ''')  # noqa

    def test_fieldwrapper_class(self):
        html_output = fieldwrapper(
            self.form['char_field'],
            fieldwrapper_class='  test class  ',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput test class">
                <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" />
            </div>
        ''')  # noqa

    def test_fieldwrapper_errors(self):
        self.form.add_error('char_field', forms.ValidationError('Err'))

        html_output = fieldwrapper(
            self.form['char_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput error">
                <input class="input-field error" id="id_char_field" name="char_field" type="text" value="abc" />
                <ul class="errorlist"><li>Err</li></ul>
            </div>
        ''')  # noqa

        html_output = fieldwrapper(
            self.form['char_field'],
            suppress_errors=True
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput ">
                <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" />
            </div>
        ''')  # noqa

    def test_fieldwrapper_help_text(self):
        html_output = fieldwrapper(
            self.form['help_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput ">
                <input class="input-field" id="id_help_field" name="help_field" type="text" value="abc" />
                <div class="helptext">Help Text</div>
            </div>
        ''')  # noqa

        self.form.add_error('help_field', forms.ValidationError('Err'))

        html_output = fieldwrapper(
            self.form['help_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput error">
                <input class="input-field error" id="id_help_field" name="help_field" type="text" value="abc" />
                <div class="helptext">Help Text</div>
                <ul class="errorlist"><li>Err</li></ul>
            </div>
        ''')  # noqa

    def test_fieldwrapper_select(self):
        html_output = fieldwrapper(
            self.form['choice_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--choicefield fieldwrapper--select ">
                <div class="select">
                    <select class="" id="id_choice_field" name="choice_field"><option selected="selected" value="1">a</option><option value="2">b</option></select>
                </div>
            </div>
        ''')  # noqa

    def test_fieldwrapper_radio_select(self):
        html_output = fieldwrapper(
            self.form['radio_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--choicefield fieldwrapper--radioselect ">
                <ul id="id_radio_field">
                    <li><label for="id_radio_field_0"><input checked="checked" class="" id="id_radio_field_0" name="radio_field" type="radio" value="1" />a</label></li>
                    <li><label for="id_radio_field_1"><input class="" id="id_radio_field_1" name="radio_field" type="radio" value="2" />b</label></li>
                </ul>
            </div>
        ''')  # noqa

    def test_fieldwrapper_checkbox(self):
        html_output = fieldwrapper(
            self.form['checkbox_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--booleanfield fieldwrapper--checkboxinput ">
                <label class="checkbox control">
                    <input checked="checked" class="" id="id_checkbox_field" name="checkbox_field" type="checkbox" />
                    <span class="control-indicator"></span>
                    <span class="control-label">
                        Checkbox field
                    </span>
                </label>
            </div>
        ''')  # noqa

        html_output = fieldwrapper(
            self.form['checkbox_field'],
            control_label='Different label',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--booleanfield fieldwrapper--checkboxinput ">
                <label class="checkbox control">
                    <input checked="checked" class="" id="id_checkbox_field" name="checkbox_field" type="checkbox" />
                    <span class="control-indicator"></span>
                    <span class="control-label">
                        Different label
                    </span>
                </label>
            </div>
        ''')  # noqa

        html_output = fieldwrapper(
            self.form['checkbox_field'],
            control_label='',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--booleanfield fieldwrapper--checkboxinput ">
                <label class="checkbox control">
                    <input checked="checked" class="" id="id_checkbox_field" name="checkbox_field" type="checkbox" />
                    <span class="control-indicator"></span>
                    <span class="control-label"></span>
                </label>
            </div>
        ''')  # noqa

        html_output = fieldwrapper(
            self.form['checkbox_help_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--booleanfield fieldwrapper--checkboxinput ">
                <label class="checkbox control">
                    <input checked="checked" class="" id="id_checkbox_help_field" name="checkbox_help_field" type="checkbox" />
                    <span class="control-indicator"></span>
                    <span class="control-label">Help Me!</span>
                </label>
            </div>
        ''')  # noqa

        html_output = fieldwrapper(
            self.form['checkbox_help_field'],
            control_label='',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--booleanfield fieldwrapper--checkboxinput ">
                <label class="checkbox control">
                    <input checked="checked" class="" id="id_checkbox_help_field" name="checkbox_help_field" type="checkbox" />
                    <span class="control-indicator"></span>
                    <span class="control-label"></span>
                </label>
                <div class="helptext">Help Me!</div>
            </div>
        ''')  # noqa

    def test_fieldwrapper_password(self):
        html_output = fieldwrapper(
            self.form['pass_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--passwordinput fieldwrapper--icon">
                <input class="input-field" id="id_pass_field" name="pass_field" type="password" />
                <button class="input-icon input-icon__password" type="button" tabindex="-1">{}</button>
            </div>
        '''.format(self.eye_svg))  # noqa

    def test_fieldwrapper_date(self):
        html_output = fieldwrapper(
            self.form['date_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--datefield fieldwrapper--dateinput fieldwrapper--icon">
                <input class="input-field" id="id_date_field" name="date_field" type="text" value="1940-10-9" />
                <label class="label--inline-edit" for="id_date_field" title="Edit Date field">{}</label>
            </div>
        '''.format(self.date_range_svg))  # noqa

    def test_fieldwrapper_field_kwargs(self):
        html_output = fieldwrapper(
            self.form['char_field'],
            **{
                'class': ' test class  ',
                'data_some': 'data',
                'placeholder': 'Fill in some test data'
            }
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput ">
               <input class="input-field test class" data-some="data" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Fill in some test data" />
            </div>
        ''')  # noqa

    def test_fieldwrapper_before_after_field(self):
        html_output = fieldwrapper(
            self.form['char_field'],
            after_field='@',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput ">
                <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" />@
            </div>
        ''')  # noqa

        html_output = fieldwrapper(
            self.form['char_field'],
            before_field='!',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput ">
                !<input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" />
            </div>
        ''')  # noqa

        html_output = fieldwrapper(
            self.form['char_field'],
            before_field='!',
            after_field='@',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput ">
                !<input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" />@
            </div>
        ''')  # noqa

        html_output = fieldwrapper(
            self.form['pass_field'],
            before_field='!',
            after_field='@',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--passwordinput fieldwrapper--icon">
                !<input class="input-field" id="id_pass_field" name="pass_field" type="password" />
                <button class="input-icon input-icon__password" type="button" tabindex="-1">{}</button>
            </div>
        '''.format(self.eye_svg))  # noqa

    def test_fieldwrapper_unit_text_left_right(self):
        html_output = fieldwrapper(
            self.form['char_field'],
            unit_text_left='$',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput fieldwrapper--unit">
               <i class="input-unit input-unit--left">$</i>
               <input class="input-field input-field--unit-left" id="id_char_field" name="char_field" type="text" value="abc" />
            </div>
        ''')  # noqa

        html_output = fieldwrapper(
            self.form['char_field'],
            unit_text_left='$',
            unit_text_right='KM',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--textinput fieldwrapper--unit">
               <i class="input-unit input-unit--left">$</i>
               <input class="input-field input-field--unit-left input-field--unit-right" id="id_char_field" name="char_field" type="text" value="abc" />
               <i class="input-unit input-unit--right">KM</i>
            </div>
        ''')  # noqa

        html_output = fieldwrapper(
            self.form['pass_field'],
            unit_text_left='$',
            unit_text_right='KM',
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper fieldwrapper--charfield fieldwrapper--passwordinput fieldwrapper--icon">
                <input class="input-field" id="id_pass_field" name="pass_field" type="password" />
                <button class="input-icon input-icon__password" type="button" tabindex="-1">{}</button>
            </div>
        '''.format(self.eye_svg))  # noqa


class FormFieldwrapperCombinedTestCase(
        DummyFormMixin, SvgIconsMixin, SimpleTestCase):
    maxDiff = None

    def test_fieldwrapper_combined(self):
        html_output = fieldwrapper_combined(
            self.form['char_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper ">
                <div class="fieldwrapper-combined">
                    <div class="fieldwrapper-combined__field fieldwrapper--charfield fieldwrapper--textinput ">
                       <input class="input-field" id="id_char_field" name="char_field" type="text" value="abc" placeholder="Char field" />
                    </div>
                </div>
            </div>
        ''')  # noqa

        html_output = fieldwrapper_combined(
            self.form['char_field'],
            self.form['int_field'],
        )
        self.assertHTMLEqual(html_output, '''
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
        ''')  # noqa

    def test_fieldwrapper_combined_class(self):
        html_output = fieldwrapper_combined(
            self.form['char_field'],
            self.form['int_field'],
            fieldwrapper_class='  test class  ',
        )
        self.assertHTMLEqual(html_output, '''
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
        ''')  # noqa

    def test_fieldwrapper_combined_errors(self):
        self.form.add_error('char_field', forms.ValidationError('Err'))

        html_output = fieldwrapper_combined(
            self.form['char_field'],
            self.form['int_field'],
        )
        self.assertHTMLEqual(html_output, '''
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
        ''')  # noqa

        self.form.add_error('int_field', forms.ValidationError('Err2'))

        html_output = fieldwrapper_combined(
            self.form['char_field'],
            self.form['int_field'],
        )
        self.assertHTMLEqual(html_output, '''
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
        ''')  # noqa

        html_output = fieldwrapper_combined(
            self.form['char_field'],
            self.form['int_field'],
            suppress_errors=True,
        )
        self.assertHTMLEqual(html_output, '''
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
        ''')  # noqa

    def test_fieldwrapper_combined_help_text(self):
        html_output = fieldwrapper_combined(
            self.form['help_field'],
            self.form['int_field'],
        )
        self.assertHTMLEqual(html_output, '''
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
        ''')  # noqa

        html_output = fieldwrapper_combined(
            self.form['help_field'],
            self.form['help_field'],
        )
        self.assertHTMLEqual(html_output, '''
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
        ''')  # noqa

        self.form.add_error('help_field', forms.ValidationError('Err'))
        self.form.add_error('int_field', forms.ValidationError('Err2'))

        html_output = fieldwrapper_combined(
            self.form['help_field'],
            self.form['int_field'],
        )
        self.assertHTMLEqual(html_output, '''
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
        ''')  # noqa

    def test_fieldwrapper_combined_select(self):
        html_output = fieldwrapper_combined(
            self.form['choice_field'],
            self.form['int_field'],
        )
        self.assertHTMLEqual(html_output, '''
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
        ''')  # noqa

    def test_fieldwrapper_combined_password(self):
        html_output = fieldwrapper_combined(
            self.form['pass_field'],
            self.form['int_field'],
        )
        self.assertHTMLEqual(html_output, '''
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
        '''.format(self.eye_svg))  # noqa

    def test_fieldwrapper_combined_date(self):
        html_output = fieldwrapper_combined(
            self.form['date_field'],
            self.form['int_field'],
        )
        self.assertHTMLEqual(html_output, '''
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
        '''.format(self.date_range_svg))  # noqa

    def test_fieldwrapper_combined_field_kwargs(self):
        html_output = fieldwrapper_combined(
            self.form['char_field'],
            self.form['int_field'],
            field0_class=' test class  ',
            field0_data_some='data',
        )
        self.assertHTMLEqual(html_output, '''
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
        ''')  # noqa

        html_output = fieldwrapper_combined(
            self.form['char_field'],
            self.form['int_field'],
            field1_class=' test class  ',
            field1_data_some='data',
        )
        self.assertHTMLEqual(html_output, '''
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
        ''')  # noqa

        html_output = fieldwrapper_combined(
            self.form['char_field'],
            self.form['int_field'],
            field0_class=' test class  ',
            field0_data_some='data',
            field1_class='test',
            field1_data_other='{}',
        )
        self.assertHTMLEqual(html_output, '''
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
        ''')  # noqa

    def test_fieldwrapper_combined_field_placeholder(self):
        html_output = fieldwrapper_combined(
            self.form['char_field'],
            self.form['int_field'],
        )
        self.assertHTMLEqual(html_output, '''
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
        ''')  # noqa

        html_output = fieldwrapper_combined(
            self.form['char_field'],
            self.form['int_field'],
            field0_placeholder='',
            field1_placeholder='',
        )
        self.assertHTMLEqual(html_output, '''
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
        ''')  # noqa

        html_output = fieldwrapper_combined(
            self.form['char_field'],
            self.form['int_field'],
            field0_placeholder='Test',
            field1_placeholder='Other',
        )
        self.assertHTMLEqual(html_output, '''
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
        ''')  # noqa

    def test_fieldwrapper_combined_before_after_field(self):
        html_output = fieldwrapper_combined(
            self.form['char_field'],
            self.form['int_field'],
            field0_before_field='!',
            field0_after_field='@',
        )
        self.assertHTMLEqual(html_output, '''
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
        ''')  # noqa

        html_output = fieldwrapper_combined(
            self.form['char_field'],
            self.form['int_field'],
            field0_before_field='!',
            field0_after_field='@',
            field1_before_field='#',
            field1_after_field='$',
        )
        self.assertHTMLEqual(html_output, '''
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
        ''')  # noqa

        html_output = fieldwrapper_combined(
            self.form['pass_field'],
            self.form['int_field'],
            field0_before_field='!',
            field0_after_field='@',  # ignored
            field1_before_field='#',
            field1_after_field='$',
        )
        self.assertHTMLEqual(html_output, '''
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
        '''.format(self.eye_svg))  # noqa

    def test_fieldwrapper_combined_unit_text_left_right(self):
        html_output = fieldwrapper_combined(
            self.form['char_field'],
            self.form['int_field'],
            field0_unit_text_left='$',
        )
        self.assertHTMLEqual(html_output, '''
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
        ''')  # noqa

        html_output = fieldwrapper_combined(
            self.form['char_field'],
            self.form['int_field'],
            field0_unit_text_left='$',
            field0_unit_text_right='KM',
            field1_unit_text_left=mark_safe('&euro;'),
        )
        self.assertHTMLEqual(html_output, '''
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
        ''')  # noqa

        html_output = fieldwrapper_combined(
            self.form['pass_field'],
            self.form['int_field'],
            field0_unit_text_left='$',
            field0_unit_text_right='KM',
            field1_unit_text_left=mark_safe('&euro;'),
        )
        self.assertHTMLEqual(html_output, '''
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
        '''.format(self.eye_svg))  # noqa

    def test_fieldwrapper_combined_uses_widget_placeholders(self):
        html_output = fieldwrapper_combined(
            self.form['int_field'],
            self.form['int_field'],
            self.form['int_field'],
            field0_placeholder='Eerste',
            field1_placeholder='Tweede',
            field2_placeholder='Derde'
        )

        html = '''
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
        '''  # noqa

        self.assertHTMLEqual(html_output, html)

        self.form.fields['int_field'].widget.attrs.update(
            placeholder='lorem ipsum')

        html_output = fieldwrapper_combined(
            self.form['int_field'],
            self.form['int_field'],
            self.form['int_field'],
            field0_placeholder='Eerste',
            field1_placeholder='Tweede',
            field2_placeholder='Derde'
        )

        self.assertHTMLEqual(html_output, html)

        html_output = fieldwrapper_combined(
            self.form['int_field'],
            self.form['int_field'],
            self.form['int_field'],
        )

        self.assertHTMLEqual(html_output, '''
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
        ''')  # noqa
