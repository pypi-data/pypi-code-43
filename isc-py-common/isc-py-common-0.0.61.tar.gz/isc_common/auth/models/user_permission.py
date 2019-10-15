import logging

from django.contrib.postgres.fields import JSONField

from isc_common.fields.related import ForeignKeyCascade
from isc_common.models.audit import AuditModel

logger = logging.getLogger(__name__)


class User_permission(AuditModel):
    user = ForeignKeyCascade("User")
    widget = ForeignKeyCascade("Widgets_trees")
    permission = JSONField(default=dict)

    def __str__(self):
        return f"{self.user.username}: {self.widget.id_widget}"

    class Meta:
        verbose_name = 'Доступы для пользователей'
        unique_together = (("user", "widget"),)

