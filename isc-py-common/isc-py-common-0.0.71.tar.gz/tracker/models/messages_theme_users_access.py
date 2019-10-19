from django.db import transaction
from django.forms import model_to_dict
from django.utils.translation import ugettext_lazy as _

import logging

from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyCascade
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditModel, AuditQuerySet, AuditManager
from tracker.models.messages_theme import Messages_theme

logger = logging.getLogger(__name__)


class MessagesThemeUsersAccessQuerySet(AuditQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class MessagesThemeUsersAccessManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'theme_id': record.theme.id,
            'user_id': record.user.id,
            'user__username': record.user.username,
            'user__first_name': record.user.first_name,
            'user__last_name': record.user.last_name,
            'user__email': record.user.email,
            'user__middle_name': record.user.middle_name,
        }
        return res

    def createFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        user_ids = data.get('user_ids', None)
        context_ids = data.get('context_ids', None)

        with transaction.atomic():
            if user_ids and context_ids:
                if not isinstance(user_ids, list):
                    user_ids = [user_ids]

                if not isinstance(context_ids, list):
                    context_ids = [context_ids]

                for user_id in user_ids:
                    for context_id in context_ids:
                        res, _ = super().get_or_create(user_id=user_id, theme_id=context_id)

            return data

    def get_queryset(self):
        return MessagesThemeUsersAccessQuerySet(self.model, using=self._db)


class MessagesThemeUsersAccess(AuditModel):
    theme = ForeignKeyCascade(Messages_theme)
    user = ForeignKeyCascade(User)

    objects = MessagesThemeUsersAccessManager()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'Доступы к темам'
