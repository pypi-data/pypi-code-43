from django.template import Context, Template
from django.test import TestCase

from terra_utils import settings


class TemplatesTagsTestCase(TestCase):
    def test_front_url(self):
        context = Context()
        template_to_render = Template(
            '{% load settings_tags %}'
            '{% front_url %}'
        )

        rendered = template_to_render.render(context)

        self.assertEqual(rendered, settings.FRONT_URL)
