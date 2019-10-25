from __future__ import unicode_literals

import os
import inspect
import subprocess

from django.db import models
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

STATUS = (('Q', _("Queued")),
          ('P', _("Processing")),
          ('D', _("Done")))

STATUS_DICT = dict(STATUS)


class Job(models.Model):
    sample = models.FileField(_("Sample"),
                              upload_to="%Y/%m/%d/samples/")
    klass_id = models.CharField(_("Class ID"), blank=True, null=True,
                                max_length=100)
    klass = models.CharField(_("Class"), max_length=100, blank=True,
                             null=True)
    features = models.CharField(_("Features"), max_length=100, blank=True,
                                null=True)
    codes = models.TextField(_("Codes"), blank=True, null=True)
    data = models.FileField(_("Data"), upload_to="%Y/%m/%d/data/",
                            blank=True, null=True)
    scale = models.BooleanField(_("Scale"), default=False)
    balance = models.BooleanField(_("Balance"), default=False)
    reduction = models.CharField(_("Reduction"), max_length=100, blank=True,
                                 null=True)
    ncomp = models.IntegerField(_("Ncomp"), blank=True, null=True)
    separability = models.BooleanField(_("Separability"), default=False)
    treatment_type = models.CharField(_("Treatment type"), max_length=100,
                                      default='classification')
    distance = models.CharField(_("Distance algorythm"), max_length=100,
                                default='euclidian')
    algorythm = models.CharField(_("Algorythm(s)"), max_length=100,
                                 blank=True, null=True)
    optimisation = models.BooleanField(_("Optimisation"), default=False)
    prediction = models.BooleanField(_("Prediction"), default=True)
    job_status = models.CharField(_("Status"), max_length=2,
                                  choices=STATUS,
                                  default='Q')
    added = models.DateTimeField(_("Added"), auto_now_add=True)
    config_filepath = models.CharField(_("Config filepath"), max_length=1000,
                                       blank=True, null=True)
    output_path = models.CharField(_("Output path"), max_length=1000,
                                   blank=True, null=True)

    class Meta:
        ordering = ('-added',)

    @property
    def status(self):
        if self.job_status in STATUS_DICT:
            return STATUS_DICT[self.job_status]
        return ''

    def write_config_to_file(self):
        directory = os.sep.join([settings.MEDIA_ROOT, str(self.added.year),
                                 str(self.added.month), str(self.added.day)])
        if not os.path.exists(directory):
            os.makedirs(directory)
        output = os.sep.join([directory, str(self.pk)])
        if not os.path.exists(output):
            os.makedirs(output)
        self.output_path = os.sep.join(
            ['media', str(self.added.year), str(self.added.month),
             str(self.added.day), str(self.pk)])
        self.config_filepath = os.sep.join([
            directory, 'config-{}.yaml'.format(self.pk)])
        self.save()
        content = render_to_string(
            'files/config.yaml',
            {'job': self, 'output': output,
             'MEDIA_ROOT': settings.MEDIA_ROOT,
             'APP_PATH': os.path.dirname(settings.BASE_DIR)})
        with open(self.config_filepath, 'w') as config_file:
            config_file.write(content)

    def treat(self):
        self.job_status = 'P'
        self.save()
        self.write_config_to_file()
        dir_app = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(
                inspect.getfile(inspect.currentframe())))))
        args = ['python', dir_app + os.sep + "run.py", '-c',
                self.config_filepath]

        if hasattr(subprocess, 'call'):
            status = subprocess.call(args)
        else:  # python3
            status = subprocess.run(args)
        self.job_status = 'D'
        self.save()
        if status == 1:
            return False
        return True
