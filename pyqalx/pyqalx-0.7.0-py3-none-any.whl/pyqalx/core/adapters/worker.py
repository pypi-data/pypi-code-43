import logging

from pyqalx.core.adapters.adapter import QalxSignalAdapter
from pyqalx.core.entities.worker import Worker
from pyqalx.core.signals import QalxWorkerSignal

logger = logging.getLogger(__name__)


class QalxWorker(QalxSignalAdapter):
    _entity_class = Worker
    signal_class = QalxWorkerSignal

    def list_endpoint(self, *args, **kwargs):
        bot_entity = kwargs.get('bot_entity', None)
        bot_endpoint = self.session.bot.detail_endpoint(guid=bot_entity['guid'])
        return f'{bot_endpoint}/{self.entity_class.entity_type}'

    def detail_endpoint(self, guid, *args, **kwargs):
        bot_entity = kwargs.get('bot_entity', None)
        bot_endpoint = self.list_endpoint(bot_entity=bot_entity)
        return f'{bot_endpoint}/{guid}'

    def get(self, guid, *args, **kwargs):
        """
        We completely override this as we don't want to send the `bot_entity`
        kwarg through to the `get` endpoint
        """
        bot_entity = kwargs.pop('bot_entity', None)
        endpoint = self.detail_endpoint(guid=guid, bot_entity=bot_entity)
        logger.debug(f"get {self.entity_class.entity_type} with guid {guid} with {endpoint}")
        resp = self._process_api_request('get', endpoint, *args, **kwargs)
        return self.entity_class(resp)

    def reload(self, entity, **kwargs):
        """
        Reloads the current entity from the API

        :param bot: An instance of ~entities.bot.Bot
        :param entity: An instance of ~entities.worker.Worker
        :return: A refreshed instance of `self.entity`
        """
        bot_entity = kwargs.get('bot_entity', None)
        guid = entity['guid']
        endpoint = self.detail_endpoint(guid=guid, bot_entity=bot_entity)
        logger.debug(f"reload {self.entity_class.entity_type} with guid {guid} with {endpoint}")
        worker_data = self._process_api_request('get', endpoint)
        return self.entity_class(worker_data)

    def update_status(self, bot_entity, entity, status):
        """
        Updates the workers status

        :param bot_entity: An instance of ~entities.bot.Bot
        :param entity: An instance of ~entities.worker.Worker
        :param status: The status to update to
        :return: None
        """
        guid = entity['guid']
        endpoint = self.detail_endpoint(guid=guid, bot_entity=bot_entity)
        logger.debug(f"update status {self.entity_class.entity_type} with guid {guid} with {endpoint}")
        self._process_api_request('patch', endpoint, status=status)

