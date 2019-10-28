import hashlib
import logging
import uuid

from django.db import transaction
from django.db.models import DateTimeField, UUIDField, CharField
from django.forms import model_to_dict
from django.utils import timezone

from isc_common import setAttr, getAttr, delAttr
from isc_common.auth.http.LoginRequets import LoginRequest
from isc_common.auth.models.user import User
from isc_common.bit import IsBitOn
from isc_common.fields.description_field import DescriptionField
from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_tree_grid_manager import CommonTreeGridManager
from isc_common.models.audit import AuditQuerySet
from isc_common.models.base_ref import Hierarcy
from tracker.models.messages_importance import Messages_importance
from tracker.models.messages_state import Messages_state
from tracker.models.messages_theme import Messages_theme

logger = logging.getLogger(__name__)


class MessagesQuerySet(AuditQuerySet):

    def create(self, **kwargs):
        setAttr(kwargs, 'checksum', hashlib.md5(kwargs.get('message').encode()).hexdigest())
        setAttr(kwargs, 'message', f'<pre>{kwargs.get("message")}</pre>')
        return super().create(**kwargs)

    def update(self, **kwargs):
        setAttr(kwargs, 'checksum', hashlib.md5(kwargs.get('message').encode()).hexdigest())
        setAttr(kwargs, 'message', f'<pre>{kwargs.get("message")}</pre>')
        return super().update(**kwargs)

    def delete(self):
        from tracker.models.messages_files_refs import Messages_files_refs
        from tracker.models.messages_files import Messages_files

        with transaction.atomic():
            for message in self:
                for messages_files_refs in Messages_files_refs.objects.filter(message_id=message.id):
                    if Messages_files_refs.objects.filter(messages_file=messages_files_refs.messages_file).count() == 1:
                        id = messages_files_refs.messages_file.id
                        messages_files_refs.delete()
                        Messages_files.objects.filter(id=id).delete()
                    else:
                        messages_files_refs.delete()

                return super().delete()


class MessagesManager(CommonTreeGridManager):

    @staticmethod
    def get_tracker_bot():
        tracker_bot, _ = User.objects.get_or_create(username='tracker_bot', last_name='Бот (Дела)', password='1234567890', props=User.props.bot, deliting=False, editing=False)
        return tracker_bot

    @staticmethod
    def getRecord(record):
        res = {
            # 'date_create': record.date_create.strftime('%d.%m.%Y, %H:%M:%S'),
            'date_create': record.date_create,
            'deliting': record.deliting,
            'editing': record.editing,
            'guid': str(record.guid).upper(),
            'id': record.id,
            'lastmodified': record.lastmodified,
            'message': record.message,
            'parent_id': record.parent_id,
            'state__name': record.state.name,
            'state_id': record.state.id,
            'theme__full_name': record.theme.full_name,
            'theme__name': record.theme.name,
            'theme_id': record.theme.id,
            'importance_id': record.importance.id if record.importance else None,
            'importance__code': record.importance.code if record.importance else None,
            'importance__name': record.importance.name if record.importance else None,
            'to_whom__short_name': record.to_whom.get_short_name,
            'to_whom__username': record.to_whom.username,
            'to_whom_id': record.to_whom.id,
            'user__color': record.user.color if record.user.color != None and record.user.color != 'undefined' else 'black',
            'user__short_name': record.user.get_short_name,
            'user__full_name': record.user.get_full_name,
            'user_id': record.user.id if record.user else None,
            'enabled': record.state.code != 'closed',
        }
        return res

    def get_queryset(self):
        return MessagesQuerySet(self.model, using=self._db)

    def createAutoErrorFromRequest(self, request, printRequest=False, function=None):
        request = DSRequest(request=request)
        data = request.get_data()
        setAttr(data, 'state', Messages_state.objects.get(code='new'))
        setAttr(data, 'theme', Messages_theme.objects.get(code='auto_from_error'))
        setAttr(data, 'to_whom', User.objects.get(username='developer'))
        message = getAttr(data, 'message', None)
        user_id = getAttr(data, 'user_id', None)
        setAttr(data, 'user', User.objects.get(id=user_id))

        if message and isinstance(message, list):
            message = '\n'.join(message)
            setAttr(data, 'message', message)
        return super().create(**data)

    @staticmethod
    def get_border(message, user=None):
        if isinstance(user, int):
            color = User.objects.get(id=user).color
            return f'<div style="border: 1px solid {color if color else "black"};" class="outline">{message}</div>'
        elif isinstance(user, User):
            return f'<div style="border: 1px solid {user.color if user.color else "black"};" class="outline">{message}</div>'
        else:
            return f'<div style="border: 1px solid "black";" class="outline">{message}</div>'

    def createFromRequest(self, request, printRequest=False, function=None):
        from tracker.models.messages_files_refs import Messages_files_refs

        request = DSRequest(request=request)
        data = request.get_data()
        data_clone = data.copy()
        messageFileIds = getAttr(data_clone, 'messageFileIds')
        delAttr(data_clone, 'messageFileIds')

        delAttr(data_clone, 'user__username')
        delAttr(data_clone, 'state__name')
        delAttr(data_clone, 'theme__full_name')
        delAttr(data_clone, 'theme__name')
        delAttr(data_clone, 'importance__name')
        delAttr(data_clone, 'isFolder')
        delAttr(data_clone, 'to_whom__username')
        delAttr(data_clone, 'user__short_name')
        delAttr(data_clone, 'to_whom__short_name')

        to_whom = getAttr(data_clone, 'to_whom')
        messages = []
        with transaction.atomic():
            if isinstance(to_whom, list):
                delAttr(data_clone, 'to_whom')

                for to_whom_id in to_whom:
                    setAttr(data_clone, 'to_whom_id', to_whom_id)
                    setAttr(data_clone, 'guid', uuid.uuid4())
                    res = super().create(**data_clone)

                    if isinstance(messageFileIds, list):
                        for messageFileId in messageFileIds:
                            Messages_files_refs.objects.get_or_create(message=res, messages_file_id=messageFileId)

                    if request.user_id != to_whom_id:
                        LoginRequest.send_bot_message(user=to_whom_id,
                                                      bot=MessagesManager.get_tracker_bot(),
                                                      message=f'<h3>Вам назначено новое дело:</h3> #{res.guid}'
                                                              f'<p>Тема: {res.theme.full_name}'
                                                              f'<p>{MessagesManager.get_border(res.message, res.user)}'
                                                              f'<p/>Статус: "{res.state.name}"'
                                                              f'<p/>Важность: "{res.importance.name}"'
                                                              f'<p/>Назначил: {res.user.get_short_name}'
                                                      )
                    messages.append(model_to_dict(res))
            else:
                setAttr(data_clone, 'guid', uuid.uuid4())
                res = super().create(**data_clone)

                if isinstance(messageFileIds, list):
                    for messageFileId in messageFileIds:
                        Messages_files_refs.objects.get_or_create(message=res, messages_file_id=messageFileId)

                if request.user_id != res.to_whom.id:
                    LoginRequest.send_bot_message(user=res.to_whom, bot=MessagesManager.get_tracker_bot(),
                                                  message=f'<h3>Вам назначено новое дело:</h3> #{res.guid}'
                                                          f'<p/>Тема: {res.theme.full_name}'
                                                          f'<p/>{MessagesManager.get_border(res.message, res.user)}'
                                                          f'<p/>Статус: "{res.state.name}"'
                                                          f'<p/>Важность: "{res.importance.name}"'
                                                          f'<p/>Назначил: {res.user.get_short_name}'
                                                  )
                messages.append(model_to_dict(res))

        return messages

    def close_rescurce(self, id, request):
        state_id = Messages_state.message_state_closed().id
        state__name = Messages_state.message_state_closed().name

        if not request.is_admin and not request.is_develop and Messages.objects.get(id=id).user.id != request.user_id:
            raise Exception(f'Закрытие может выполнить только автор.')

        for message in Messages.objects.filter(parent_id=id):
            message.state_id = state_id
            message.save()

            if request.user_id != message.to_whom.id:
                user = User.objects.get(id=request.user_id)
                LoginRequest.send_bot_message(user=message.to_whom.id, bot=MessagesManager.get_tracker_bot(),
                                              message=f'<h3>Изменение дела:</h3> #{message.guid}'
                                                      f'<p/>Тема: {message.theme.full_name}'
                                                      f'<p/>{MessagesManager.get_border(message.message, user)}'
                                                      f'<p/>Статус: "{state__name}"'
                                                      f'<p/>Важность: "{message.importance.name}"'
                                                      f'<p/>Изменил: {user.get_short_name}'
                                              )
            self.close_rescurce(message.id, request)

    def updateFromRequest(self, request, printRequest=False):
        from tracker.models.messages_files_refs import Messages_files_refs

        request = DSRequest(request=request)
        data = request.get_data()
        old_data = request.get_oldValues()

        data_clone = data.copy()
        messageFileIds = getAttr(data_clone, 'messageFileIds')
        delAttr(data_clone, 'messageFileIds')
        delAttr(data_clone, 'user__username')
        delAttr(data_clone, 'user__short_name')
        delAttr(data_clone, 'to_whom__short_name')

        delAttr(data_clone, 'state__name')

        theme__full_name = getAttr(data_clone, 'theme__full_name')
        delAttr(data_clone, 'theme__full_name')
        delAttr(data_clone, 'theme__name')
        delAttr(data_clone, 'importance__name')
        delAttr(data_clone, 'importance__code')
        delAttr(data_clone, 'enabled')

        delAttr(data_clone, 'id')
        delAttr(data_clone, 'isFolder')
        delAttr(data_clone, 'parent')
        id = request.get_id()

        old_to_whom_id = old_data.get('to_whom_id')
        to_whom_id = data.get('to_whom_id')

        if old_to_whom_id != to_whom_id:
            setAttr(data_clone, 'user_id', request.user_id)
            setAttr(data_clone, 'parent_id', id)
            setAttr(data_clone, 'guid', uuid.uuid4())
            setAttr(data, 'message', old_data.get('message'))

            with transaction.atomic():
                res = super().create(**data_clone)

                if isinstance(messageFileIds, list):
                    for messageFileId in messageFileIds:
                        Messages_files_refs.objects.get_or_create(message=res, messages_file_id=messageFileId)

                LoginRequest.send_bot_message(user=to_whom_id,
                                              bot=MessagesManager.get_tracker_bot(),
                                              message=f'<h3>Вам назначено новое дело:</h3>#{getAttr(data_clone, "guid")}'
                                                      f'<p/>Тема: {theme__full_name}'
                                                      f'<p/>{MessagesManager.get_border(data_clone.get("message"), res.user)}'
                                                      f'<p/>Статус: "{Messages_state.objects.get(id=data_clone.get("state_id")).name}"'
                                                      f'<p/>Важность: "{Messages_importance.objects.get(id=data_clone.get("importance_id")).name}"'
                                                      f'<p/>Назначил: {res.user.get_short_name}'
                                              )
        else:
            with transaction.atomic():
                res = super().filter(id=id).update(
                    importance_id=data_clone.get('importance_id'),
                    message=data_clone.get('message'),
                    state_id=data_clone.get('state_id'),
                    to_whom_id=data_clone.get('to_whom_id'),
                )

                if isinstance(messageFileIds, list):
                    for message in Messages.objects.filter(id=id):
                        for messageFileId in messageFileIds:
                            Messages_files_refs.objects.get_or_create(message=message, messages_file_id=messageFileId)

                if res > 0:
                    user_id = None
                    if request.user_id != data_clone.get('to_whom_id'):
                        user_id = data_clone.get('to_whom_id')

                    if request.user_id != data_clone.get('user_id'):
                        user_id = data_clone.get('user_id')

                    if user_id:
                        user = User.objects.get(id=request.user_id)
                        LoginRequest.send_bot_message(user=user_id,
                                                      bot=MessagesManager.get_tracker_bot(),
                                                      message=f'<h3>Изменение дела:</h3>#{data_clone.get("guid")}'
                                                              f'<p/>Тема: {data.get("theme__full_name")}'
                                                              f'<p/>{MessagesManager.get_border(data.get("message"), user)}'
                                                              f'<p/>Cтатус: "{Messages_state.objects.get(id=data_clone.get("state_id")).name}"'
                                                              f'<p/>Важность: "{Messages_importance.objects.get(id=data_clone.get("importance_id")).name}"'
                                                              f'<p/>Изменил: {user.get_short_name}')

                    if data_clone.get('state_id') == Messages_state.message_state_closed().id:
                        setAttr(data, 'enabled', False)
                        self.close_rescurce(id, request)

        return data

    def deleteFromRequest(self, request, removed=None, ):
        from tracker.models.messages_files_refs import Messages_files_refs
        request = DSRequest(request=request)
        res = 0
        tuple_ids = request.get_tuple_ids()
        with transaction.atomic():
            for id, mode in tuple_ids:
                if mode == 'hide':
                    message = super().get(id=id)
                    if not request.is_admin and not request.is_develop and message.user.id != request.user_id:
                        raise Exception(f'Удаление может выполнить только автор.')
                    message.soft_delete()
                else:
                    message = super().get(id=id)
                    if not request.is_admin and not request.is_develop and message.user.id != request.user_id:
                        raise Exception(f'Удаление может выполнить только автор.')

                    Messages_files_refs.objects.filter(message=message).delete()
                    qty, _ = message.delete()

                    if request.user_id != message.user.id:
                        user = User.objects.get(id=request.user_id)
                        if not IsBitOn(message.user.props, 0):
                            LoginRequest.send_bot_message(user=message.to_whom.id,
                                                          bot=MessagesManager.get_tracker_bot(),
                                                          message=f'<h3>Удаление дела:</h3> #{message.guid}'
                                                                  f'<p/>Тема: {message.theme.full_name}'
                                                                  f'<p/>{MessagesManager.get_border(message.message, user)}'
                                                                  f'<p/>Статус: "{message.state.name}"'
                                                                  f'<p/>Важность: "{message.importance.name if message.importance else None}"'
                                                                  f'<p/>Удалил: {user.get_short_name}'
                                                      )
                    res += qty
        return res


class Messages(Hierarcy):
    checksum = CharField(max_length=255)
    guid = UUIDField(blank=True, null=True)
    message = DescriptionField(null=False, blank=False)
    date_create = DateTimeField(verbose_name='Дата записи', db_index=True, default=timezone.now)
    user = ForeignKeyCascade(User, related_name='user_msg_user')
    theme = ForeignKeyProtect(Messages_theme)
    importance = ForeignKeyProtect(Messages_importance, blank=True, null=True)
    state = ForeignKeyCascade(Messages_state)
    to_whom = ForeignKeyCascade(User, related_name='user_msg_to_whom')

    def __str__(self):
        return f'id: {self.id}, guid: {str(self.guid).upper()}, message: {self.message}, date_create: {self.date_create}, user: [{self.user}], theme: [{self.theme}], state: [{self.state}]'

    objects = MessagesManager()

    class Meta:
        verbose_name = 'Сообщения'
        unique_together = (('guid', 'theme', 'state', 'checksum', 'user', 'to_whom'),)
        ordering = ('date_create',)
