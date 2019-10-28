import logging

from isc_common.models.base_ref import BaseRef

logger = logging.getLogger(__name__)


class Messages_state(BaseRef):
    def __str__(self):
        return f"id: {self.code}, id: {self.code}, name: {self.name}, description: {self.description}"

    class Meta:
        verbose_name = 'Состояние задачи'

    @staticmethod
    def message_state_new():
        return Messages_state.objects.get_or_create(code="new", defaults=dict(name='Новый'))[0]

    @staticmethod
    def message_state_closed():
        return Messages_state.objects.get_or_create(code="closed", defaults=dict(name='Закрыто'))[0]

    @staticmethod
    def message_state_delivered():
        return Messages_state.objects.get_or_create(code="delivered", defaults=dict(name='Доставлено'))[0]

    @staticmethod
    def message_state_readed():
        return Messages_state.objects.get_or_create(code="readed", defaults=dict(name='Прочитано'))[0]
