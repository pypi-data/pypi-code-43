import logging

from django.db import transaction

from isc_common import delAttr, setAttr
from isc_common.auth.models.user import User
from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyCascade
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_tree_grid_manager import CommonTreeGridManager
from isc_common.models.base_ref import BaseRefHierarcy

logger = logging.getLogger(__name__)


class Messages_theme_Manager(CommonTreeGridManager):
    @staticmethod
    def getRecord(record):
        res = {
            "id": record.id,
            "code": record.code,
            "name": record.name,
            # "full_name": record.full_name,
            "description": record.description,
            "parent_id": record.parent_id,
            "lastmodified": record.lastmodified,
            "editing": record.editing,
            "deliting": record.deliting,
        }
        return res

    def createFromRequest(self, request):
        from tracker.models.messages_theme_users_access import MessagesThemeUsersAccess

        user_id = request.session._session.get('user_id')
        _request = DSRequest(request=request)
        data = _request.get_data()
        _data = data.copy()
        delAttr(_data, 'isFolder')
        delAttr(_data, 'full_name')
        setAttr(_data, 'creator_id', user_id)
        res = super().create(**_data)

        MessagesThemeUsersAccess.objects.get_or_create(theme=res, user_id=user_id)
        return data

    def updateFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()

        _list = [value for key, value in data.items()]
        is_list_of_dict = len([a for a in _list if isinstance(a, dict)]) > 0
        if is_list_of_dict:
            with transaction.atomic():
                for _data in _list:
                    if isinstance(_data, dict):
                        delAttr(_data, 'isFolder')
                        delAttr(_data, 'full_name')
                        delAttr(_data, 'children')
                        res = super().filter(id=_data.get('id')).update(**_data)
        else:
            delAttr(data, 'isFolder')
            delAttr(data, 'full_name')
            delAttr(data, 'children')
            res = super().filter(id=data.get('id')).update(**data)
        return res


class Messages_theme(BaseRefHierarcy):
    code = CodeField(unique=True)
    creator = ForeignKeyCascade(User, null=True, blank=True)

    @staticmethod
    def auto_from_error():
        return Messages_theme.objects.get_or_create(
            code='auto_from_error',
            defaults=dict(
                name='Автоматически занесенные из сообщений об ошибках.',
                creator=User.admin_user(),
                editing=False,
                deliting=False,
                description='Тема создана автоматически'))[0]

    @staticmethod
    def chats_theme():
        return Messages_theme.objects.get_or_create(
            code='chats',
            defaults=dict(
                name='Сообщения чатов',
                creator=User.admin_user(),
                editing=False,
                deliting=False,
                description='Тема создана автоматически'))[0]

    @staticmethod
    def group_chats_theme():
        return Messages_theme.objects.get_or_create(
            code='group_chats',
            defaults=dict(
                name='Групповые чаты',
                creator=User.admin_user(),
                editing=False,
                deliting=False,
                parent=Messages_theme.chats_theme(),
                description='Тема создана автоматически'))[0]

    @staticmethod
    def tetatet_chats_theme():
        return Messages_theme.objects.get_or_create(
            code='tetatet_chats',
            defaults=dict(
                name='Чаты личной переписки',
                creator=User.admin_user(),
                editing=False,
                deliting=False,
                parent=Messages_theme.chats_theme(),
                description='Тема создана автоматически'))[0]

    @staticmethod
    def system_chats_theme():
        return Messages_theme.objects.get_or_create(
            code='system_chats',
            defaults=dict(
                name='Чаты системных сообщений',
                creator=User.admin_user(),
                editing=False,
                deliting=False,
                parent=Messages_theme.chats_theme(),
                description='Тема создана автоматически'))[0]

    def __str__(self):
        return f"id: {self.code}, id: {self.code}, name: {self.name}, description: {self.description}"

    objects = Messages_theme_Manager()

    class Meta:
        verbose_name = 'Темы задач'
