from django.db import models

from .base import RedminModel


class Group(RedminModel):
    class Meta:
        verbose_name_plural = verbose_name = "用户组"

    name = models.CharField('名称', max_length=50)

    def __str__(self):
        return self.name
