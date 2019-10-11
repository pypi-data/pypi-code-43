from django.contrib.postgres.fields import JSONField
from django.db import models


class DummyModel(models.Model):
    name = models.CharField(max_length=250)
    properties = JSONField(default=dict)
