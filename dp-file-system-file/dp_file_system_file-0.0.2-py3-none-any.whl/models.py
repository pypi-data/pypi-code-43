from django.db import models


class FSFile(models.Model):

    name = models.TextField(blank=False, null=False)
    creation_date = models.DateTimeField(
        blank=True, null=True, auto_now_add=True)
    modification_date = models.DateTimeField(
        blank=True, null=True, auto_now=True)
    size = models.IntegerField(blank=False, null=True)
    mime_type = models.CharField(max_length=100, blank=False, null=False)
    # Full path to the file
    path = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'dp_file_system_file'
