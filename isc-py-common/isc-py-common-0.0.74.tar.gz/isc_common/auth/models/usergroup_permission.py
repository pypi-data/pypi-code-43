import logging

from django.contrib.postgres.fields import JSONField

from isc_common.fields.related import ForeignKeyCascade
from isc_common.models.audit import AuditModel

logger = logging.getLogger(__name__)


class Usergroup_permission(AuditModel):
    usergroup = ForeignKeyCascade("UserGroup")
    widget = ForeignKeyCascade("Widgets_trees")
    permission = JSONField(default=dict)

    # def __str__(self):
    #     return f"{self.code}: {self.name}"

    class Meta:
        verbose_name = 'Доступы для групп'
        unique_together = (("usergroup", "widget"),)
