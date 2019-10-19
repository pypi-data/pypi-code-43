from django.db import models


class DynamicModelEntity(models.Model):
    def __str__(self):
        return self.label

    class Meta:
        abstract = True

    label = models.CharField(max_length=255)

