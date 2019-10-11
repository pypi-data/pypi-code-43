# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from collections import OrderedDict
import uuid
import json
from django.utils.translation import ugettext_lazy as _
from django.utils.six import python_2_unicode_compatible
from django.utils.six.moves.urllib.parse import parse_qs
from django.urls import reverse
from django.db import models
import django.dispatch
from adminsortable.models import SortableMixin
from adminsortable.fields import SortableForeignKey
from .utils import Utils


input_notification = django.dispatch.Signal(providing_args=['input_data', 'input_type', 'input_id'])


@python_2_unicode_compatible
class InputSettings(models.Model):
    FORMATS = [
        ('form', _("Form")),
        ('json', _("JSON"))
    ]
    uid = models.UUIDField(_("UID"), max_length=60, unique=True, default=uuid.uuid4,
        editable=False)
    name = models.CharField(_("Name"), max_length=60, unique=True)
    description = models.TextField(_("Description"), blank=True, default='')
    default_format = models.CharField(_("Default format"), max_length=60,
        default='json', choices=FORMATS)

    class Meta:
        verbose_name = _("Input settings")
        verbose_name_plural = _("Input settings")

    def __str__(self):
        return self.name

    def update_field_definitions(self):
        """Updates input settings field definitions from the last created
        input of this settings.
        """
        input = self.inputs.last()
        if input:
            input.update_field_definitions()
            return input
        return False


@python_2_unicode_compatible
class InputSettingsField(SortableMixin):
    # orderable info
    settings = SortableForeignKey(InputSettings, verbose_name=_("Input settings"),
        related_name='input_fields', on_delete=models.CASCADE)
    field_position = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    # transformation info
    input_name = models.CharField(_("Input name"), max_length=60)
    output_name = models.CharField(_("Field name"), max_length=60, blank=True, default='')
    example_value = models.TextField(_("Example value"), blank=True, default='')
    date_format = models.CharField(_("Date format"), max_length=40, blank=True, default='')
    default_value = models.TextField(_("Default value"), blank=True, default='')
    exclude_if_empty = models.BooleanField(_("Exclude if empty"), blank=True, default=False)
    omit = models.BooleanField(_("Omit"), blank=True, default=False)

    class Meta:
        verbose_name = _("Input field")
        verbose_name_plural = _("Input fields")
        ordering = ['field_position']
        unique_together = [('settings', 'input_name')]

    def __str__(self):
        return self.input_name

class Input(models.Model):
    "Input data."
    settings = models.ForeignKey(InputSettings, verbose_name=_("Settings"),
        blank=False, null=False, on_delete=models.PROTECT,
        related_name='inputs')
    internal_source = models.BooleanField(_("Internal source"), blank=True,
        default=True)
    format = models.CharField(_("Default format"), max_length=60, default='json',
        choices=InputSettings.FORMATS)
    processed = models.BooleanField(_("Processed"), blank=True, default=False)
    raw_content = models.TextField(_("Raw content"))
    created = models.DateTimeField(_("Created"), auto_now_add=True, blank=True, null=True)
    modified = models.DateTimeField(_("Modified"), auto_now=True, blank=True, null=True)

    class Meta:
        verbose_name = _("Input")
        verbose_name_plural = _("Inputs")

    def get_raw_dict(self):
        if self.format == 'json':
            return json.loads(self.raw_content)
        if self.format == 'form':
            result = parse_qs(self.raw_content)
            return dict((key, value[0]) for key, value in result.items())
        raise ValueError("Input format not supported: {}".format(self.format))

    def update_field_definitions(self):
        for key, value in self.get_raw_dict().items():
            try:
                field = InputSettingsField.objects.get(settings=self.settings,
                    input_name=key)
                field.example_value = str(value)
                field.save()
            except InputSettingsField.DoesNotExist:
                field = InputSettingsField()
                field.settings = self.settings
                field.input_name = key
                field.example_value = str(value)
                field.save()

    def get_data(self):
        raw_dict = self.get_raw_dict()
        if self.settings.input_fields.all().count() == 0:
            return raw_dict
        result = OrderedDict()
        for field in InputSettingsField.objects.filter(settings=self.settings):
            if field.omit:
                continue
            if field.input_name in raw_dict:
                value = raw_dict[field.input_name]
                if field.date_format:
                    value = datetime.datetime.strptime(value, field.date_format)
                Utils.write_to_dict(result, field.output_name or field.input_name, value)
            elif not field.exclude_if_empty:
                Utils.write_to_dict(result, field.output_name or field.input_name,
                    field.default_value or None)
        return result

    def notify(self):
        input_notification.send_robust(sender=self.__class__, input_data=self.get_data(),
            input_type=self.settings.uid, input_id=self.pk)



@python_2_unicode_compatible
class Webhook(models.Model):
    uid = models.UUIDField(_("UID"), max_length=60, unique=True, default=uuid.uuid4,
        editable=False)
    name = models.CharField(_("Name"), max_length=60, unique=True)
    description = models.TextField(_("Description"), blank=True, default='')
    settings = models.ForeignKey(InputSettings, verbose_name=_("Settings"),
        blank=False, null=False, on_delete=models.CASCADE, related_name='webhooks')

    class Meta:
        verbose_name = _("Webhook")
        verbose_name_plural = _("Webhooks")

    def __str__(self):
        return self.name

    def get_webhook_url(self):
        return reverse('inputflow:inputflow-webhook', args=(self.uid,))

