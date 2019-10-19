import logging

from django.forms import model_to_dict

from isc_common import setAttr, delAttr, getAttr
from isc_common.auth.managers.base_user_manager import BaseUserManager
from isc_common.auth.models.usergroup import UserGroup
from isc_common.bit import IsBitOn
from isc_common.http.DSRequest import DSRequest

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    use_in_migrations = True

    @staticmethod
    def getRecord(**kwargs):
        record = kwargs.get('record')
        res = {
            "id": record.id,
            "username": record.username,
            "description": record.description,
            "first_name": record.first_name,
            "last_name": record.last_name,
            "email": record.email,
            "middle_name": record.middle_name,
            "short_name": record.get_short_name,
            "short_name1": record.get_short_name1,
            "password": record.password,
            "last_login": record.last_login,
            "lastmodified": record.lastmodified,
            "editing": record.editing,
            "deliting": record.deliting,
            "color": record.color,
            "bot": IsBitOn(record.props, 0),
        }
        return res

    def updateFromRequest(self, request, printRequest=False):
        request = DSRequest(request=request)
        data = request.get_data()
        delAttr(data, 'usergroup')
        oldValues = request.get_oldValues()

        _oldValues = getAttr(oldValues, 'data')
        if not _oldValues:
            _oldValues = oldValues

        values = [item for item in list(set(_oldValues) - set(data)) if not item.startswith('_')]
        for item in values:
            setAttr(data, item, None)

        user_id = request.get_id()

        delAttr(data, 'short_name1')
        delAttr(data, 'status')
        delAttr(data, 'timer')
        delAttr(data, 'timer4Close')
        delAttr(data, 'ws')
        delAttr(data, 'grid')
        delAttr(data, 'short_name')
        delAttr(data, 'bot')

        super().filter(id=user_id).update(**data)

        if data.get('password', None) != getAttr(_oldValues, 'password'):
            user = self.model.objects.get(pk=user_id)
            user.set_password(data.get('password', None))
            user.save()
            user = self.model.objects.get(pk=user_id)
            setAttr(data, 'password', user.password)
            setAttr(data, 'short_name', user.get_short_name)

        return data

    def createFromRequest(self, request, printRequest=False):
        request = DSRequest(request=request)
        data = request.get_data(excluded_keys=['id'])
        usergroup_id = data.get('usergroup_id')
        delAttr(data, 'usergroup_id')
        delAttr(data, 'on_line')
        user = super().create(**self.clone_data(data))
        password = request.get_data(excluded_keys=['id']).get('password', None)
        user = self.model.objects.get(pk=user.id)
        user.set_password(password)
        user.save(using=self._db)
        user = self.model.objects.get(pk=user.id)
        if isinstance(usergroup_id, list):
            for group in usergroup_id:
                user.usergroup.add(group)
        res = model_to_dict(user)
        setAttr(res, 'props', res.get('props')._value)
        return self.clone_data(res)

    def _create_user(self, usergroup, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')

        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        if isinstance(usergroup, list):
            user.usergroup.set(usergroup)
        elif isinstance(usergroup, UserGroup):
            user.usergroup.set([usergroup])

        return user

    def create_user(self, usergroup, username, email=None, password=None, **extra_fields):
        try:
            return self.model.objects.get(username=username)
        except self.model.DoesNotExist:
            return self._create_user(usergroup, username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        try:
            return self.model.objects.get(username=username)
        except self.model.DoesNotExist:
            return self._create_user(usergroup=UserGroup.objects.get(code='administrators'), username=username, email=email, password=password, **extra_fields)
