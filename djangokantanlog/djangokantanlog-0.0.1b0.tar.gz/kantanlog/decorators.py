# -*- coding: utf8 -*-
from django.db import models


def cbyuby(cls):
    """
    Usage:

    .. code:: python

      @cbyuby
      class MyModel(modles.Model):
        ...
    """

    cby = models.CharField(
        verbose_name='created by',
        null=False,
        blank=False,
        max_length=100,
        default='',
    )

    uby = models.CharField(
        verbose_name='updated by',
        null=False,
        blank=False,
        max_length=100,
        default='',
    )

    cat = models.DateTimeField(
        auto_now_add=True,
        null=True
    )

    uat = models.DateTimeField(
        auto_now=True,
        null=True
    )

    cls.add_to_class('created_by', cby)
    cls.add_to_class('updated_by', uby)
    cls.add_to_class('created_at', cat)
    cls.add_to_class('updated_at', uat)

    return cls
