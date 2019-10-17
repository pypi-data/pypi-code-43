from django.contrib.auth.models import AbstractUser
from django.db import models

from .base import RedminModel
from .group import Group


class User(AbstractUser, RedminModel):
    class Meta:
        verbose_name_plural = verbose_name = "用户"

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    title = models.CharField('名称', max_length=50, blank=False, null=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.username
        return super().save(*args, **kwargs)
