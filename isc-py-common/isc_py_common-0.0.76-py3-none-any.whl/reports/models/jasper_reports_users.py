import logging

from django.db import transaction

from isc_common import delAttr
from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyCascade
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditModel, AuditManager
from reports.models.jasper_reports import Jasper_reports

logger = logging.getLogger(__name__)


class AuditModelQuerySet(object):
    pass


class Jasper_reports_usersQuerySet(AuditModelQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Jasper_reports_usersManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'user_id': record.user.id,
            'user__username': record.user.username,
            'user__first_name': record.user.first_name,
            'user__last_name': record.user.last_name,
            'user__email': record.user.email,
            'user__middle_name': record.user.middle_name,
        }
        return res

    def get_queryset(self):
        return Jasper_reports_usersQuerySet(self.model, using=self._db)

    def updateFromRequest(self, request, removed=None, function=None):
        request = DSRequest(request=request)
        data = request.get_data()
        _data = data.copy()

        delAttr(_data, 'id')
        delAttr(_data, 'user__username')
        delAttr(_data, 'user__first_name')
        delAttr(_data, 'user__last_name')
        delAttr(_data, 'user__email')
        delAttr(_data, 'user__middle_name')

        res = super().filter(id=data.get('id')).update(**_data)
        return data

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
                        res, _ = super().get_or_create(user_id=user_id, report_id=context_id)

            return data


class Jasper_reports_users(AuditModel):
    report = ForeignKeyCascade(Jasper_reports)
    user = ForeignKeyCascade(User)

    objects = Jasper_reports_usersManager()

    def __str__(self):
        return f"ID:{self.id}, code: {self.code}, name: {self.name}, description: {self.description}"

    class Meta:
        verbose_name = 'Доступ пользователей к отчетам'
