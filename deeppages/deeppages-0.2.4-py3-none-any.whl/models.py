from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.urls import resolve, reverse, Resolver404

from autoslug import AutoSlugField
from autoslug.settings import slugify as default_slugify


class Template(models.Model):
    ''' Deep Pages' Template model '''
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text=('Unique template name. Relative path can be used, ie.: '
                   'dashboard/index.html'))

    content = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField('Created At', auto_now_add=True)
    changed_at = models.DateTimeField('Changed At', auto_now=True)

    class Meta:
        verbose_name = 'Template'
        verbose_name_plural = 'Templates'

    def __str__(self):
        return self.name


class Page(models.Model):
    ''' Deep Pages' Page Model - store pages with its own paths (urls) '''
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text=_('This name will be used to identify the page. Ex.: my '
                    'page name'))

    slug = AutoSlugField(
        slugify=default_slugify,
        always_update=True,
        populate_from='name',
        unique=True,
        help_text=_('Unique identifier to be used on imports and other '
                    'references'))

    path = models.CharField(
        max_length=100,
        help_text=_('Type the absolute path. Ex.: /my-page-name/'))

    content = models.TextField(null=True, blank=True, default=None)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    changed_at = models.DateTimeField('Changed At', auto_now=True)

    class Meta:
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')
        ordering = ('name',)
        get_latest_by = 'changed_at'

    def _validate_path(self):
        try:
            resolved = resolve(self.path)

        except Resolver404:
            return True

        else:
            # Check if it's a deep pages' view answer
            if resolved.func.view_class.__module__ == 'deeppages.views':
                return True
            # ignore url if Wagtail CMS is being used and serving for urls.
            # as long Wagtail uses url patterns to serve pages and deep pages
            # can be used serving by Middleare, I'm assuming the Wagtail isn't
            # interfering in deep page's behaviorsl
            if resolved.url_name == 'wagtail_serve':
                return True
            else:
                return self.path != reverse('deeppages:__deep_page_view__')

    def __str__(self):
        return f'{self.pk}: {self.name} ({self.slug})'

    def render(self, context=None, callback=None):
        from .utils import render_content
        ctx = context or {}
        return render_content(self.content, ctx)

    def save(self, *args, **kwargs):
        if not self._validate_path():
            print(_('This PATH is already being used. Try a different path.'))
            return False
        else:
            return super().save(*args, **kwargs)
