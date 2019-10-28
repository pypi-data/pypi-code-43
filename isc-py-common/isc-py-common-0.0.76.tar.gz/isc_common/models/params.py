import datetime
import logging

import dateutil.parser
from django.db.models import TextField
from django.forms import model_to_dict

from isc_common import getAttr, setAttr
from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyCascade
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditModel, AuditQuerySet, AuditManager

logger = logging.getLogger(__name__)


class ParamsQuerySet(AuditQuerySet):
    def get_params(self, request, *args):
        request = DSRequest(request=request)
        data = request.get_data()
        app_id = getAttr(data, 'app_id')

        try:
            periodEraseHistory = int(super().get(user_id=getAttr(data, 'user_id'), key=f'periodEraseHistory{app_id}').value)
        except Params.DoesNotExist:
            periodEraseHistory = 1
            super().create(user_id=getAttr(data, 'user_id'), key=f'periodEraseHistory{app_id}', value=periodEraseHistory)

        lastEraseHistory = None
        try:

            lastEraseHistory = super().get(user_id=getAttr(data, 'user_id'), key=f'lastEraseHistory{app_id}').value
            lastEraseHistory = dateutil.parser.parse(lastEraseHistory)
            delta = datetime.datetime.now() - lastEraseHistory
        except Params.DoesNotExist:
            delta = None

        if not delta or delta.days > periodEraseHistory:
            super().filter(user_id=getAttr(data, 'user_id'), key__icontains='_ComboBoxItemSS').delete()
            if not lastEraseHistory:
                super().create(user_id=getAttr(data, 'user_id'), key=f'lastEraseHistory{app_id}', value=datetime.datetime.now())
            else:
                super().filter(user_id=getAttr(data, 'user_id'), key=f'lastEraseHistory{app_id}', value=lastEraseHistory).update(value=datetime.datetime.now())

        queryResult = super().filter(user_id=getAttr(data, 'user_id'))
        res = [model_to_dict(record) for record in queryResult]
        return res


class ParamsManager(AuditManager):
    def get_queryset(self):
        return ParamsQuerySet(self.model, using=self._db)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'key': record.key[1:len(record.key) - 1] if record.key[0:1] == "'" else record.key,
            'value': record.value,
            'lastmodified': record.lastmodified,
        }
        return res

    def deleteFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        ids = []
        if data:
            ids = [param.id for param in Params.objects.filter(user=getAttr(data, 'user_id'), key=getAttr(data, 'key'))]

        if len(ids) == 0:
            ids = request.get_ids()
        res = super().filter(id__in=ids).delete()
        return res[0]

    def update1FromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        key = getAttr(data, 'key')
        value = getAttr(data, 'value')
        user_id = getAttr(data, 'user_id')

        res = data
        if key != None and user_id != None:
            if key[0:1] == "'":
                key = key[1:len(key) - 1]
            setAttr(data, 'key', key)

            if value == None or value == '':
                res = super().filter(
                    user_id=user_id,
                    key=key
                ).delete()
            else:
                res, _ = super().update_or_create(
                    user_id=user_id,
                    key=key,
                    defaults=dict(value=value)
                )
                res = model_to_dict(res)
        return res


class Params(AuditModel):
    user = ForeignKeyCascade(User)
    key = TextField()
    value = TextField(null=True, blank=True)

    objects = ParamsManager()

    def __str__(self):
        return f"{self.key}: {self.value}"

    class Meta:
        verbose_name = 'Сохраненные параметры'
        unique_together = (('user', 'key'),)
