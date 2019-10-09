""" Cerebro Service """
import requests
from loguru import logger

class CerebroService:
    """ A service for interacting with Cerebro """

    def __init__(self, cerebro_url: str):
        logger.debug(f'Initializing new Cerebro Service for URL {cerebro_url}')
        self._cerebro_url = cerebro_url

    def started(self, task_id: str, **kwargs):
        """ Tells Cerebro that a Task has started """
        logger.info(f'Telling Cerebro that Task(id={task_id}) has started')
        requests.post(
            url=f'{self._cerebro_url}/tasks/{task_id}/started',
            data=kwargs
        )

    def finished(self, task_id: str, **kwargs):
        """ Tells Cerebro that a Task has finished """
        logger.info(f'Telling Cerebro that Task (id={task_id}) has finished')
        requests.post(
            url=f'{self._cerebro_url}/tasks/{task_id}/finished',
            data=kwargs
        )

    def errored(self, task_id: str, message: str):
        """ Tells Cerebro that a Task has errored """
        logger.info(f'Telling Cerebro that Task (id={task_id}) has errored')
        requests.post(
            url=f'{self._cerebro_url}/tasks/{task_id}/errored',
            json={"message": message}
        )

    def message(self, task_id: str, message: str):
        """ Updates a Task's message """
        logger.info(f'Updating Cerebro Task (id={task_id}) message')
        requests.post(
            url=f'{self._cerebro_url}/tasks/{task_id}',
            json={'message': message}
        )
