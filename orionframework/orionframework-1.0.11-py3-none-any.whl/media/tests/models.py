from django.db.models.base import Model
from django.db import models
from orionframework.media.services import ServiceImage


class MyProduct(Model):
    name = models.CharField(max_length=50)

    def __init__(self, *args, **kwargs):
        Model.__init__(self, *args, **kwargs)

        self.images = ServiceImage(parent=self, category=0)
        self.defects = ServiceImage(parent=self, category=1)
