from django.db import models


class Foo(models.Model):

    bar = models.CharField(max_length=10)

    class Meta:
        verbose_name = 'Foo'
        verbose_name_plural = 'Foo'
