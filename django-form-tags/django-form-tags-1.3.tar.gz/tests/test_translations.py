from django.test.testcases import SimpleTestCase
from django.utils.translation import activate

from form_tags.templatetags.forms import fieldwrapper_combined

from .mixins import DummyFormMixin, SvgIconsMixin


class FormFieldwrapperCombinedTestCase(
        DummyFormMixin, SvgIconsMixin, SimpleTestCase):
    maxDiff = None

    # TODO add fieldwrapper

    # TODO add fieldholder_inline

    def test_fieldwrapper_date_label_title_translation(self):
        activate('en')
        html_output = fieldwrapper_combined(
            self.form['date_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper ">
                <div class="fieldwrapper-combined">
                    <div class="fieldwrapper-combined__field fieldwrapper--datefield fieldwrapper--dateinput fieldwrapper--icon">
                        <input class="input-field" id="id_date_field" name="date_field" type="text" value="1940-10-9" placeholder="Date field" />
                        <label class="label--inline-edit" for="id_date_field" title="Edit Date field">{}</label>
                    </div>
                </div>
            </div>
        '''.format(self.date_range_svg))  # noqa

        activate('nl')
        html_output = fieldwrapper_combined(
            self.form['date_field'],
        )
        self.assertHTMLEqual(html_output, '''
            <div class="fieldwrapper ">
                <div class="fieldwrapper-combined">
                    <div class="fieldwrapper-combined__field fieldwrapper--datefield fieldwrapper--dateinput fieldwrapper--icon">
                        <input class="input-field" id="id_date_field" name="date_field" type="text" value="1940-10-9" placeholder="Date field" />
                        <label class="label--inline-edit" for="id_date_field" title="Date field wijzigen">{}</label>
                    </div>
                </div>
            </div>
        '''.format(self.date_range_svg))  # noqa
