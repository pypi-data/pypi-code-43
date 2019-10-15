from django.db import models
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class ID4meStore(models.Model):
    authority = models.CharField(max_length=255)
    context = models.TextField()

    def __str__(self):
        return self.authority

