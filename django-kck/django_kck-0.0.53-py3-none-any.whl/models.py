from django.db import models
from picklefield.fields import PickledObjectField


class DataProduct(models.Model):
    """the cache table"""
    key = models.CharField(max_length=1024, primary_key=True)
    value = PickledObjectField()
    primer_name = models.CharField(max_length=1024, db_index=True, null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    modified = models.DateTimeField(auto_now_add=True)
    soft_expire = models.DateTimeField(null=True, blank=True)
    hard_expire = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('primer_name', 'key')


class RefreshQueue(models.Model):
    key = models.CharField(max_length=1024)
    hints = PickledObjectField(blank=True, null=True)
    primer_name = models.CharField(max_length=1024, db_index=True)
    claimant = models.CharField(max_length=64, null=True, blank=True)
    claimed = models.DateTimeField(null=True, blank=True)
    requested = models.DateTimeField(auto_now_add=True)
