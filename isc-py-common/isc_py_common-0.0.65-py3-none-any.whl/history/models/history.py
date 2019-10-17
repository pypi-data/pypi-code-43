import logging

from django.contrib.postgres.fields import JSONField
from django.db.models import Model, DateTimeField
from django.utils import timezone
from isc_common.fields.code_field import CodeField
from isc_common.fields.name_field import NameField

logger = logging.getLogger(__name__)


class History(Model):
    date = DateTimeField(db_index=True, default=timezone.now)
    method = CodeField()
    path = CodeField()
    username = NameField()
    data = JSONField(default=dict)

    def __str__(self):
        return f"method: {self.method} path: {self.path} data{self.data}"

    class Meta:
        verbose_name = 'History'
