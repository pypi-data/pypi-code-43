from django.db import models

from .base import RedminModel
from .domain import Domain


class Menu(RedminModel):
    class Meta:
        ordering = ["sequence"]
        verbose_name_plural = verbose_name = "菜单"

    name = models.CharField("名称", max_length=100, unique=True)
    sequence = models.IntegerField("排序", default=0)

    def __str__(self):
        return self.name


class DomainMenu(RedminModel):
    class Meta:
        ordering = ["menu__sequence", "domain__sequence"]
        verbose_name_plural = verbose_name = "模型菜单"
        unique_together = [('menu', 'domain')]

    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)

    def __str__(self):
        return f"DomainMenu({self.id}-{self.menu.name}-{self.domain.name})"
