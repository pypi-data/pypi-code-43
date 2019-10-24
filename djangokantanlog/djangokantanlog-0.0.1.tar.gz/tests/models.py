# -*- coding: utf8 -*-
from django.db import models
from kantanlog.decorators import cbyuby


@cbyuby
class TObject(models.Model):

    name = models.CharField(
        verbose_name="name",
        max_length=100,
        unique=True,
        null=False,
        blank=False,
    )

    level = models.IntegerField(
        verbose_name="level",
        null=False,
        blank=False,
    )

    def __str__(self):
        return ("%s, %s, %s" % (self.name, self.created_by, self.updated_by))
