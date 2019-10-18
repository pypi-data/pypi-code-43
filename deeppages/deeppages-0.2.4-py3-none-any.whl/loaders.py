from django.template import Origin, TemplateDoesNotExist
from django.template.loaders.base import Loader

from .models import Template


class DatabaseLoader(Loader):
    ''' Custom template loader that loads templates from database and is
    managed by model Page.
    '''
    def get_contents(self, origin):
        try:
            template = Template.objects.get(pk=origin.name)
        except Template.DoesNotExist:
            raise TemplateDoesNotExist(origin)
        else:
            return template.content

    def get_template_sources(self, template_name):
        """
        Return an Origin object pointing to an absolute path in each directory
        in template_dirs. For security reasons, if a path doesn't lie inside
        one of the template_dirs it is excluded from the result set.
        """
        try:
            template = Template.objects.get(name=template_name)
        except Template.DoesNotExist:
            pass
        else:
            yield Origin(
                name=template.pk,
                template_name=template_name,
                loader=self
            )
